# -*- coding: utf-8 -*-
import maya.cmds as cmds
import moon.channel


def _get_source_and_target():
    """선택된 객체를 대상으로 Source, Target 오브젝트를 알아내어 반환해준다"""
    selected = cmds.ls(selection=True)
    if len(selected) == 2:
        return selected[0], selected[1]
    else:
        return None, None


def _get_target_clone(target):
    """타겟의 복제품을 만든다. 타겟의 채널에 여러가지 커넥션이 있을 수 있기 때문에 깨끗한 오브젝트를 만드는 것이다."""
    target_clone = cmds.duplicate(target)[0]
    for ch in moon.channel.DEFAULT_CHANNELS:
        cmds.setAttr(target_clone + '.' + ch, lock=False, keyable=True)
    parent = cmds.listRelatives(target_clone, parent=True)
    if parent:
        cmds.parent(target_clone, world=True)

    return target_clone


def match_transform(source=None, target=None):
    """
    첫 번째 선택한 대상을 두 번째 선택한 대상에게 포지션, 로테이션 값을 복제해서
    두 대상의 위치와 회전량을 일치시켜주는 기능
    """
    if not source or not target:
        source, target = _get_source_and_target()
    if source and target:
        # target_clone = _get_target_clone(target)
        # cmds.delete(cmds.parentConstraint(target_clone, source, maintainOffset=False))
        # cmds.delete(target_clone)
        match_position(source, target)
        match_rotation(source, target)


def match_position(source=None, target=None):
    """
    첫 번째 선택한 대상을 두 번째 선택한 대상에게 포지션 값만 복제해서
    두 대상의 위치를 일치시켜주는 기능
    """
    if not source or not target:
        source, target = _get_source_and_target()
    if source and target:
        # target_clone = _get_target_clone(target)
        # cmds.delete(cmds.pointConstraint(target_clone, source, maintainOffset=False))
        # cmds.delete(target_clone)
        trans = cmds.xform(target, query=True, worldSpace=True, rotatePivot=True)
        cmds.move(trans[0], trans[1], trans[2], source, rotatePivotRelative=True, moveXYZ=True)


def match_rotation(source=None, target=None):
    """
    첫 번째 선택한 대상을 두 번째 선택한 대상에게 로테이션 값만 복제해서
    두 대상의 최전량을 일치시켜주는 기능
    """
    if not source or not target:
        source, target = _get_source_and_target()
    if source and target:
        # target_clone = _get_target_clone(target)
        # cmds.delete(cmds.orientConstraint(target_clone, source, maintainOffset=False))
        # cmds.delete(target_clone)
        rot = cmds.xform(target, query=True, worldSpace=True, rotation=True)
        cmds.rotate(rot[0], rot[1], rot[2], source, worldSpace=True, absolute=True, rotateXYZ=True)


def match_scale(source=None, target=None):
    """
    첫 번째 선택한 대상을 두 번째 선택한 대상에게 스케일 값만 복제해서
    두 대상의 크기를 일치시켜주는 기능
    """
    if not source or not target:
        source, target = _get_source_and_target()
    if source and target:
        scale = cmds.xform(target, query=True, worldSpace=True, scale=True)
        cmds.xform(source, worldSpace=True, scale=scale)
