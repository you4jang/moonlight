# -*- coding: utf-8 -*-
import os
import sys
import maya.cmds as cmds


def init_paths():
    from moon.join import pathjoin

    # 모든 패스에 대한 정보를 가지게 될 path 사전 정의
    path = {}

    # 인하우스툴의 저장소가 될 네트워크 드라이브 이름
    tools_drive = 'z:'

    # 인하우스툴의 루트 경로 이름
    tools_root_name = 'moonlight'

    # 인하우스툴의 경로
    tools_root_path = pathjoin(tools_drive, tools_root_name)

    # 개발자의 소스가 들어갈 네트워크 드라이브 이름
    dev_path = None
    for drive in ['c', 'd']:
        p = pathjoin('{}:'.format(drive), 'dev', tools_root_name)
        if os.path.isdir(p):
            dev_path = p
            break

    # 개발자의 인하우스툴의 위치를 먼저 파악하고, 존재할 경우 그 패스를 우선으로 설정한다.
    if dev_path:
        path['home'] = dev_path
    # 개발자의 자리가 아니라고 판단되면 서버의 인하우스툴의 위치로 지정한다.
    else:
        path['home'] = tools_root_path

    # 인하우스툴의 소스 경로가 지정되었으므로,
    # 그 밖에 반드시 설정이 되어야만 하는 경로들을 추가로 설정한다.
    additional_paths = [
        pathjoin(path['home'], 'lib'),
    ]

    for p in additional_paths:
        sys.path.append(p)

    import moon.context
    moon.context.add('tools_root_path', path['home'])


def customize_shelf_tab_layout():
    if cmds.about(batch=True):
        return

    # 마야 메인 쉘프 레이아웃의 높이를 조절할 수 있는 모듈
    import moon.menu.shelftab
    moon.menu.shelftab.restore()


def customize_pulldown_menu():
    if cmds.about(batch=True):
        return

    import moon.menu.pulldown
    moon.menu.pulldown.create()


def init_preferences():
    if cmds.about(batch=True):
        return

    # 레퍼런스로 불러온 데이터에 대해서 채널 편집을 할 수 있도록 허용하는 옵션
    cmds.optionVar(intValue=("refLockEditable", 1))

    # 마야 바이너리 파일을 읽어올 때 버전이 맞지 않더라도 읽을 수 있도록 허용하는 옵션
    cmds.optionVar(intValue=("fileIgnoreVersion", 1))


def init_color_management():
    if cmds.about(batch=True):
        return

    cmds.colorManagementPrefs(edit=True, cmEnabled=True)
