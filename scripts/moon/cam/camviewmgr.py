# -*- coding: utf-8 -*-
from moon.qt import *
from moon.path import dirs
from moon.join import attrjoin

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import os

import moon.scriptjob
import moon.modelpanel
reload(moon.modelpanel)


class SeparatedCameraPanelWindow(QDialog):

    def __init__(self, parent=maya_widget()):
        super(SeparatedCameraPanelWindow, self).__init__(parent)
        # 패널을 삭제해주는 MEL을 로딩한다.
        mel.eval('source deletePanel')
        self.ui()

    def resizeEvent(*args, **kwargs):
        store_window(args[0])

    def moveEvent(*args, **kwargs):
        store_window(args[0])

    def closeEvent(*args, **kwargs):
        moon.scriptjob.remove_script_job(__name__)

    def ui(self):
        self.win = 'separated_camera_panel_window'
        self.setObjectName(self.win)
        self.setWindowTitle('Camera View Manager')
        self.setWindowIcon(QIcon(img_path('bean_ci_icon.png')))
        self.setFont(MAIN_FONT)

        # 윈도우 레이아웃
        self.window_layout = QVBoxLayout(self)
        self.window_layout.setAlignment(Qt.AlignTop)
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(0)

        # 메인 레이아웃
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(9, 20, 9, 9)
        self.main_layout.setSpacing(6)

        # 평면 카메라 리스트
        ortho_grp = QGroupBox('Orthographic')
        ortho_grp_layout = QVBoxLayout(ortho_grp)
        self.ortho_list = CameraViewList(self)
        ortho_grp_layout.addWidget(self.ortho_list)

        # 퍼스펙티브 카메라 리스트
        persp_grp = QGroupBox('Perspective')
        persp_grp_layout = QVBoxLayout(persp_grp)
        self.persp_list = CameraViewList(self)
        persp_grp_layout.addWidget(self.persp_list)

        ####################################################################################################
        # 윈도우 레이아웃 배치
        ####################################################################################################
        self.main_layout.addWidget(persp_grp)
        self.main_layout.addItem(QSpacerItem(0, 20))
        self.main_layout.addWidget(ortho_grp)

        self.window_layout.addLayout(self.main_layout)

        # 창의 사이즈를 만들어진 컨트롤러들의 크기에 꼭 맞춰준다.
        self.adjustSize()
        self.setMinimumWidth(250)
        restore_window(self)
        self.setFocus()

        ####################################################################################################
        # 스타트업 메소드
        ####################################################################################################
        self.append_cam_to_list()
        self.scriptjob()

    def scriptjob(self):
        cmds.scriptJob(conditionTrue=('delete', self.append_cam_to_list))
        cmds.scriptJob(event=('DagObjectCreated', self.append_cam_to_list))
        cmds.scriptJob(event=('NewSceneOpened', self.append_cam_to_list))
        cmds.scriptJob(event=('PostSceneRead', self.append_cam_to_list))
        cmds.scriptJob(event=('SceneOpened', self.append_cam_to_list))
        cmds.scriptJob(event=('NameChanged', self.append_cam_to_list))

    def append_cam_to_list(self):
        self.ortho_list.clear()
        self.persp_list.clear()

        orthocam = cmds.listCameras(orthographic=True)
        for cam in orthocam:
            if cmds.nodeType(cam) == 'camera':
                cam = cmds.listRelatives(cam, parent=True)[0]
            self.ortho_list.addItem(cam)

        perspcam = cmds.listCameras(perspective=True)
        for cam in perspcam:
            if cmds.nodeType(cam) == 'camera':
                cam = cmds.listRelatives(cam, parent=True)[0]
            self.persp_list.addItem(cam)


class CameraViewList(QListWidget):

    CLONE_PREFIX = 'CLONE'

    def __init__(self, parent=None):
        super(CameraViewList, self).__init__(parent)
        self.parent = parent
        self.clicked.connect(self.on_camera_selected)

    def on_camera_selected(self):
        selected = self.currentItem().text()
        pm.select(selected, replace=True)

    def contextMenuEvent(self, event, *args, **kwargs):
        """마우스 우클릭 컨텍스트 메뉴 이벤트 재정의"""
        # 현재 선택된 카메라가 무엇인지 파악한다.
        current_item = self.currentItem()

        # 컨텍스트 메뉴 정의
        menu = QMenu(self)
        menu.setFont(MAIN_FONT)

        tearoff_panel_action = menu.addAction('별도 패널 분리')
        duplicate_panel_action = menu.addAction('카메라 복사 후 별도 패널 분리')
        menu.addSeparator()
        action_cam_bake_abc = menu.addAction('카메라 베이크')

        action_delete = None

        # 선택된 카메라가 마야에서 기본으로 제공하는 카메라일 경우 컨텍스트 메뉴를 만들지 않는다.
        if current_item.text() not in ['top', 'side', 'front', 'persp']:
            menu.addSeparator()
            action_delete = menu.addAction('삭제')

        # 입력 받은 액션 반환
        action = menu.exec_(self.mapToGlobal(event.pos()))

        # 각 액션 별로 필요한 메소드 호출
        if action == tearoff_panel_action:
            self.tearoff_panel()
        elif action == duplicate_panel_action:
            self.duplicate_panel()
        elif action is not None and action == action_delete:
            self.delete_panel()
        elif action == action_cam_bake_abc:
            self.bake(alembic=True)

    def mouseDoubleClickEvent(self, *args, **kwargs):
        """마우스로 더블-클릭 했을 때의 이벤트 재정의"""
        selected = self.currentItem().text()
        cmds.lookThru(selected)
        cmds.headsUpMessage('Current Camera : {0}'.format(selected), time=1)

    @staticmethod
    def _get_panel_name_by_cam(cam):
        """주어진 카메라를 이용하여 패널 윈도우에 들어갈 모델패널 이름을 지정하고 반환한다"""
        return '{0}_tearoff_modelpanel'.format(cam.split(':')[-1])

    def _get_window_name_by_cam(self, cam):
        """주어진 카메라를 이용하여 패널 윈도우의 이름을 지정하고 반환한다"""
        return '{}_{}'.format(self.parent.win, cam)

    def tearoff(self, cam):
        """지정한 카메라의 패널을 분리하여 주는 메소드"""
        win = self._get_window_name_by_cam(cam)
        modelpanel = self._get_panel_name_by_cam(cam)
        # 패널용 윈도우가 이미 있을 경우 삭제한다.
        if cmds.window(win, exists=True):
            cmds.deleteUI(win, window=True)
        # 지정한 카메라의 모든 모델패널을 삭제한다.
        if cmds.modelPanel(modelpanel, exists=True):
            moon.modelpanel.delete(modelpanel)
        # 새로운 패널용 윈도우 생성
        cmds.window(win, sizeable=True, title='MV Camera View Manager (Separated) :: {0}'.format(cam))
        cmds.paneLayout()
        # 새로운 모델 패널 생성
        cmds.modelPanel(modelpanel, label=modelpanel, camera=cam, menuBarVisible=True)
        # 생성한 모델패널의 기본적인 패널 뷰 속성을 꾸며준다.
        self.set_modeleditor_nice(modelpanel)
        # 윈도우의 크기는 기본적으로 800, 600으로 한다.
        cmds.window(win, edit=True, width=800, height=600)
        cmds.showWindow(win)

    def tearoff_panel(self):
        """선택한 카메라의 패널을 분리해서 생성해준다"""
        sel = self.currentItem().text()
        self.tearoff(sel)

    def duplicate_panel(self):
        """선택한 카메라의 패널을 복사해서 분리해준다"""
        sel = self.currentItem().text()
        self.create_new_panel_with_appended_camera(sel)

    def delete_panel(self):
        """선택한 패널과 해당하는 카메라를 삭제해준다"""
        # 선택된 카메라
        current_item = self.currentItem()
        cam = current_item.text()
        # 사용자에게 보여줄 메시지 화면을 구성한다.
        msg = Message()
        msg.title('카메라 삭제')
        msg.add('선택한 카메라를 삭제하시겠습니까?')
        msg.br()
        msg.add('선택한 카메라 :')
        msg.add_filename(cam)
        msg.end()
        # 선택할 수 있는 버튼을 구성한다.
        buttons = ok, cancel = '삭제', '취소'
        # 사용자에게 메시지를 보여준다.
        confirm = questionbox(
            parent=self,
            title='카메라 삭제',
            message=msg.output(),
            button=buttons,
            cancel=cancel,
            dismiss=cancel,
            default=cancel
        )
        # 취소를 선택하면 실행을 종료한다.
        if confirm == cancel:
            return
        # 카메라가 포함된 모델패널이 있을 경우 삭제한다.
        moon.modelpanel.delete_by_cam(cam)
        # 카메라를 삭제한다.
        cmds.delete(cam)
        # 카메라를 위해서 Tear Off 된 윈도우나 패널이 있다면 삭제한다.
        win = self._get_window_name_by_cam(cam)
        if cmds.window(win, exists=True):
            cmds.deleteUI(win, window=True)
        # 목록을 다시 만든다.
        self.parent.append_cam_to_list()

    def create_new_panel_with_appended_camera(self, cam):
        """선택한 카메라를 복제하여 새로운 카메라를 만들고, 새로운 패널도 만들어서 만든 패널에 새로운 카메라를 붙여주는 메소드"""
        new_cam = cmds.duplicate(cam, name='{}_{}'.format(self.CLONE_PREFIX, cam))
        # visibility 채널을 Off 해야하는데 해당 채널이 잠겨있을 수도 있기 때문에 검사를 해봐야 한다.
        visattr = new_cam[0] + '.visibility'
        locked = False
        if cmds.getAttr(visattr, lock=True):
            cmds.setAttr(visattr, lock=False)
            locked = True
        cmds.setAttr('{}.visibility'.format(new_cam[0]), False)
        if locked:
            cmds.setAttr(visattr, lock=True)
        self.tearoff(new_cam[0])

    @staticmethod
    def set_modeleditor_nice(modelpanel):
        cmds.modelEditor(modelpanel, edit=True, activeView=True)
        cmds.modelEditor(modelpanel, edit=True, allObjects=False)
        cmds.modelEditor(modelpanel, edit=True, selectionHiliteDisplay=False)
        cmds.modelEditor(modelpanel, edit=True, grid=False)
        cmds.modelEditor(modelpanel, edit=True, polymeshes=True)
        cmds.modelEditor(modelpanel, edit=True, subdivSurfaces=True)
        cmds.modelEditor(modelpanel, edit=True, pluginShapes=True)
        cmds.modelEditor(modelpanel, edit=True, strokes=True)
        cmds.modelEditor(modelpanel, edit=True, displayAppearance='smoothShaded')
        cmds.modelEditor(modelpanel, edit=True, displayTextures=False)
        cmds.modelEditor(modelpanel, edit=True, selectionHiliteDisplay=False)

    def bake(self, alembic=True):
        pm.loadPlugin('AbcExport', quiet=True)

        buttons = export, create, cancel = '.abc 저장', '씬 안에 생성', '취소'
        option = questionbox(
            parent=self,
            title='출력형태 지정',
            message='베이크할 카메라의 출력 형태를 선택하세요.',
            icon='question',
            button=buttons,
            default=export,
            cancel=cancel,
            dismiss=cancel,
        )
        if option == cancel:
            return

        cam_file = None
        file_type = None

        if option == export:
            optionvar = 'camviewmgr_last_exported_path'

            if pm.optionVar(exists=optionvar):
                last_dir = pm.optionVar(query=optionvar)
            else:
                last_dir = ''

            response = QFileDialog.getSaveFileName(
                caption='카메라가 저장될 위치를 지정하세요',
                dir=last_dir,
                filter='Alembic File (*.abc)',
                parent=self,
            )
            if not response[0]:
                return
            cam_file = response[0]
            dirs(os.path.dirname(cam_file))
            pm.optionVar(stringValue=(optionvar, os.path.dirname(cam_file)))

        cam = pm.PyNode(self.currentItem().text())
        if not cam:
            return
        cam_shape = cam.getShape()

        pm.undoInfo(openChunk=True)

        dup_cam = pm.duplicate(cam)[0]
        dup_cam_shape = dup_cam.getShape()

        for child in pm.listRelatives(dup_cam, children=True):
            if child.nodeType() == 'camera':
                continue
            pm.delete(child)

        cam_shape.focalLength.connect(dup_cam_shape.focalLength, force=True)
        cam_shape.nearClipPlane.connect(dup_cam_shape.nearClipPlane, force=True)
        cam_shape.farClipPlane.connect(dup_cam_shape.farClipPlane, force=True)

        dup_cam_shape.focalLength.set(lock=False, keyable=True)
        dup_cam_shape.nearClipPlane.set(lock=False, keyable=True)
        dup_cam_shape.farClipPlane.set(lock=False, keyable=True)

        for child in pm.listRelatives(dup_cam, children=True):
            if child.nodeType() == 'camera':
                continue
            pm.delete(child)

        for ch in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            attr = dup_cam.attr(ch)
            attr.set(lock=False)

        for attr in dup_cam.listAttr(userDefined=True):
            try:
                attr.set(lock=False)
                pm.deleteAttr(attr)
            except:
                pass

        pm.parent(dup_cam, world=True)
        pm.rename(dup_cam, cam.name() + '_baked')
        constraint = pm.parentConstraint(cam, dup_cam)
        st = pm.playbackOptions(query=True, minTime=True - 2)
        ed = pm.playbackOptions(query=True, maxTime=True + 2)
        # pm.bakeResults(
        #     [dup_cam, dup_cam_shape],
        #     shape=True,
        #     simulation=True,
        #     time=(st, ed),
        # )
        pm.delete(constraint)

        pm.undoInfo(closeChunk=True)

        if cam_file:
            pm.rename(dup_cam, cam.name())
            pm.select(dup_cam, replace=True)
            pm.delete(pm.ls(type='unknown'))
            pm.mel.eval('AbcExport -j "-frameRange {} {} -noNormals -eulerFilter -dataFormat ogawa -root {} -file {}"'.format(st, ed, dup_cam.name(), cam_file))
            # cmds.file(
            #     cam_file,
            #     force=True,
            #     options="v=0;",
            #     type=file_type,
            #     preserveReferences=True,
            #     exportSelected=True,
            # )
            if option != create:
                pm.delete(dup_cam)


def main():
    global camviewmgrwin

    try:
        camviewmgrwin.close()
        camviewmgrwin.deleteLater()
    except:
        pass

    camviewmgrwin = SeparatedCameraPanelWindow()
    camviewmgrwin.show()
