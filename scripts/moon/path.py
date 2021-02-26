# -*- coding: utf-8 -*-
import os
import maya.cmds as cmds
import maya.mel as mel


def basenameex(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def dirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def open_folder(path):
    if os.path.isdir(path):
        os.startfile(path)


def set_retaining_path(path):
    optionvar = mel.eval('$g_dir_retain_ov = $gDirRetainingOptionVar')
    cmds.optionVar(stringValue=(optionvar, path))


def add_recent_file(filename):
    if os.path.isfile(filename):
        mel.eval('addRecentFile("{}", "mayaBinary")'.format(filename))


def set_workspace(path):
    cmds.workspace(path, openWorkspace=True)


def save_changes(parent=None):
    """
    열려있는 씬 파일에 변동사항이 있는지 검사하여, 변동사항이 있을 경우 사용자에게 파일 저장 여부를 묻고,
    그에 따른 결과를 반환해주는 메소드
    """
    if not cmds.file(query=True, anyModified=True):
        return True
    
    filename = cmds.file(query=True, sceneName=True)
    if not filename:
        filename = 'untitled scene'
    buttons = save, dontsave, cancel = 'Save', 'Do not Save', 'Cancel'
    confirm = cmds.confirmDialog(
        title='Warning: Scene Not Saved',
        message='Save changes to {}?'.format(filename),
        button=buttons,
        defaultButton=save,
        cancelButton=cancel,
        dismissString=cancel,
    )
    
    if confirm == cancel:
        return
        
    if confirm == save:
        if not filename:
            getfilename = cmds.fileDialog2(
                returnFilter=True,
                caption='Save As',
                fileMode=0,
                okCaption=save,
                selectFileFilter='Maya Binary',
                fileFilter='Maya ASCII (*.ma);;Maya Binary (*.mb)',
                startingDirectory=cmds.workspace(cmds.workspace(fullName=True), query=True, directory=True)
            )
            if not getfilename:
                return
            cmds.file(rename=getfilename[0])
        cmds.file(save=True)
    elif confirm == dontsave:
        return True
