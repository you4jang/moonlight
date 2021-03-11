# -*- coding: utf-8 -*-
import maya.cmds as cmds


DEFAULT_VISIBLE_CHANNEL = 'v'

####################################################################################################
# 기본 채널에 대한 상수 정의
####################################################################################################
TX = 'translateX'
TY = 'translateY'
TZ = 'translateZ'
RX = 'rotateX'
RY = 'rotateY'
RZ = 'rotateZ'
SX = 'scaleX'
SY = 'scaleY'
SZ = 'scaleZ'
VISIBILITY = 'visibility'

TRANSLATE = [TX, TY, TZ]
ROTATE = [RX, RY, RZ]
SCALE = [SX, SY, SZ]

DEFAULT_CHANNELS = [TX, TY, TZ, RX, RY, RZ, SX, SY, SZ]
ALL_CHANNELS = DEFAULT_CHANNELS + [VISIBILITY]


def v_channel(node):
    """주어진 노드의 Visibility 채널 이름을 반환해주는 함수"""
    return node + '.' + VISIBILITY


def _attrname(node, channel):
    """주어진 노드 이름과 채널 이름으로 연결용 속성이름을 반환한다.
    
    :param str node: 노드 이름
    :param str channel: 채널 이름
    """
    return node + '.' + channel


def _shapename(node):
    """주어진 노드의 쉐입 이름을 반환한다.
    
    :param str node: 노드 이름
    """
    result = []
    shapes = cmds.listRelatives(node, shapes=True)
    if shapes:
        result += shapes
    return result


def lock(node, shape=True, visible=False, userdefined=False):
    """주어진 노드의 주어진 채널 종류들을 모두 잠근다.
    
    :param str node: 노드 이름
    :param bool shape: 카메라의 쉐입 노드도 잠글 것인지 여부
    :param bool visible: 기본 채널 중 Visibility 채널도 잠글 것인지 여부
    :param bool userdefined: 사용자가 만든 채널도 잠글 것인지 여부
    """
    nodes = [node]
    if shape:
        nodes += _shapename(node)
    
    for nd in nodes:
        target_channels = list()
        unlocked = cmds.listAttr(nd, keyable=True, unlocked=True)
        if unlocked:
            for unlock_ch in unlocked:
                if unlock_ch not in target_channels:
                    target_channels.append(unlock_ch)
        channelbox = cmds.listAttr(nd, channelBox=True, unlocked=True)
        if channelbox:
            for cb_ch in channelbox:
                if cb_ch not in target_channels:
                    target_channels.append(cb_ch)
        if userdefined:
            user_ch = cmds.listAttr(nd, userDefined=True)
            if user_ch:
                target_channels += user_ch
        for channel in target_channels:
            if cmds.objExists(_attrname(nd, channel)):
                try:
                    cmds.setAttr(_attrname(nd, channel), lock=True)
                except:
                    continue


def hide(node, shape=True, visible=False, userdefined=False):
    """주어진 노드의 주어진 채널 종류를 모두 숨긴다.

    :param str node: 노드 이름
    :param bool shape: 카메라의 쉐입 노드도 잠글 것인지 여부
    :param bool visible: 기본 채널 중 Visibility 채널도 잠글 것인지 여부
    :param bool userdefined: 사용자가 만든 채널도 잠글 것인지 여부
    """
    nodes = [node]
    if shape:
        nodes += _shapename(node)
    
    for nd in nodes:
        target_channels = cmds.listAttr(nd)
        for channel in target_channels:
            if cmds.objExists(_attrname(nd, channel)):
                try:
                    cmds.setAttr(_attrname(nd, channel), keyable=False, channelBox=False)
                except:
                    continue


def set_attr(nodes, channels, keyable=False, lock=False):
    if not isinstance(nodes, list) and not isinstance(nodes, tuple):
        nodes = [nodes]
    if not isinstance(channels, list) and not isinstance(channels, tuple):
        channels = [channels]
    for n in nodes:
        for ch in channels:
            if not cmds.objExists(n + '.' + ch):
                continue
            cmds.setAttr(n + '.' + ch, lock=lock, keyable=keyable)
