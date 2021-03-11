# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


def __get_panel():
    panels = cmds.getPanel(type='modelPanel')
    focus = cmds.getPanel(withFocus=True)
    if focus in panels:
        return focus
    pointer = cmds.getPanel(underPointer=True)
    if pointer in panels:
        return pointer


def to_wireframe():
    for panel in pm.getPanel(type='modelPanel'):
        pm.modelEditor(panel, edit=True, displayAppearance='wireframe')


def to_bounding_box():
    for panel in pm.getPanel(type='modelPanel'):
        pm.modelEditor(panel, edit=True, displayAppearance='boundingBox')


def toggle_wireframe_on_shaded():
    panel = __get_panel()
    if not panel:
        return
    wos = pm.modelEditor(panel, query=True, wireframeOnShaded=True)
    pm.modelEditor(panel, edit=True, wireframeOnShaded=not wos)


def find_by_cam(cam):
    """주어진 카메라를 이용하여 해당 카메라가 사용되고 있는 모델 패널의 이름을 리스트로 반환한다"""
    result = []
    camshape = None
    if cmds.nodeType(cam) == 'camera':
        camshape = cam
        cam = cmds.listRelatives(camshape, parent=True)[0]
    else:
        # 카메라 쉐입의 이름을 알아온다.
        for child in cmds.listRelatives(cam, shapes=True):
            if cmds.nodeType(child) == 'camera':
                camshape = child
                break
    # 모든 modelPanel 타입의 패널을 알아온다.
    for panel in cmds.getPanel(type='modelPanel'):
        # 각 패널의 이름을 토대로 카메라의 이름을 알아낸다.
        cam_on_panel = cmds.modelPanel(panel, query=True, camera=True)
        # 패널에 속한 카메라가 카메라 쉐입일 수도 있고 카메라 트랜스폼 일 수도 있다.
        if cam == cam_on_panel:
            result.append(panel)
        if camshape == cam_on_panel:
            result.append(panel)

    return result


def delete(modelpanel):
    """주어진 모델패널을 MEL을 이용하여 안전하게 삭제한다.
    모델패널을 지우는 것은 MEL을 이용하여 삭제하는 것이 가장 안전하다.
    """
    mel.eval('source "deletePanel.mel"')
    mel.eval('deletePanelNoConfirm("{}")'.format(modelpanel))


def delete_by_cam(cam):
    """주어진 카메라를 이용하여 해당 카메라가 사용하고 있는 모델 패널 전부를 삭제한다.
    deletePanel이라는 MEL을 이용해서 삭제하는 것이 마야의 크러쉬를 해결하고, 깔끔하게 삭제할 수 있는 방법이다.
    """
    for panel in find_by_cam(cam):
        delete(panel)
