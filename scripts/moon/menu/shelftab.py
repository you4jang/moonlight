# -*- coding: utf-8 -*-
import maya.cmds as cmds
import pymel.core as pm


__all__ = ['increase', 'decrease', 'reset', 'restore']


def increase(step):
    ShelfTabLayout.increase(step)


def decrease(step):
    ShelfTabLayout.decrease(step)


def reset():
    ShelfTabLayout.reset()


def restore():
    ShelfTabLayout.restore()


class ShelfTabLayout(object):

    SHELF_LAYOUT = 'ShelfLayout'
    OPTION_VAR = 'CustomizedShelfLayoutHeight'

    @classmethod
    def increase(cls, step):
        height = pm.shelfTabLayout(cls.SHELF_LAYOUT, query=True, height=True) + step
        cls.set_height(height)

    @classmethod
    def decrease(cls, step):
        height = pm.shelfTabLayout(cls.SHELF_LAYOUT, query=True, height=True) - step
        if height < 64:
            height = 64
        cls.set_height(height)

    @classmethod
    def reset(cls):
        cls.set_height(64)

    @classmethod
    def restore(cls):
        if pm.optionVar(exists=cls.OPTION_VAR):
            try:
                height = pm.optionVar(query=cls.OPTION_VAR)
                cls.set_height(height)
            except:
                cls.reset()
        else:
            cls.reset()

    @classmethod
    def set_height(cls, height):
        print('new height : {}'.format(height))
        pm.shelfTabLayout(cls.SHELF_LAYOUT, edit=True, height=height)
        pm.optionVar(intValue=(cls.OPTION_VAR, height))


class ShelfTab(object):

    # 생성하려는 커스터마이징 쉘프 레이아웃 조절용 메뉴 아이템의 이름 정의
    MAIN_TAGS = [
        'ShelfLayoutCustomResizeDivisionMenuItem',
        'ShelfLayoutCustomResizeIncreaseMenuItem',
        'ShelfLayoutCustomResizeDecreaseMenuItem',
        'ShelfLayoutCustomResizeDefaultMenuItem',
    ]

    def __init__(self):
        pass

    @classmethod
    def _get_shelf_layout_root_popup(cls):
        popups = cmds.lsUI(type='popupMenu')
        if not popups:
            return
        for i, popup in enumerate(popups):
            if not popup:
                continue
            try:
                menus = cmds.popupMenu(popup, query=True, itemArray=True)
                if menus:
                    for menu in menus:
                        if 'Shelf Editor...' == cmds.menuItem(menu, query=True, label=True):
                            return popup
            except:
                pass

    @classmethod
    def add_shelf_layout_resizing_menus(cls):
        print('add_shelf_layout_resizing_menus()')
        # 커스터마이징용으로 생성된 메뉴 아이템들을 일단 모두 지운다.
        popup = cls._get_shelf_layout_root_popup()
        if popup:
            menu_items = cmds.popupMenu(popup, query=True, itemArray=True)
            for item in menu_items:
                tag = cmds.menuItem(item, query=True, docTag=True)
                if cls.MAIN_TAGS[0] in tag:
                    cmds.deleteUI(item, menuItem=True)
                if cls.MAIN_TAGS[1] in tag:
                    cmds.deleteUI(item, menuItem=True)
                if cls.MAIN_TAGS[2] in tag:
                    cmds.deleteUI(item, menuItem=True)
                if cls.MAIN_TAGS[3] in tag:
                    cmds.deleteUI(item, menuItem=True)
        # 마야 쉘프 레이아웃의 루트 팝업 메뉴을 알아낸다.
        popup = cls._get_shelf_layout_root_popup()
        # 각 기능을 가진 메뉴 아이템들을 루트 팝업 메뉴에 추가한다.
        cmds.menuItem(parent=popup, divider=True, docTag=cls.MAIN_TAGS[0])
        cmds.menuItem(parent=popup, label='Shelf Line +', docTag=cls.MAIN_TAGS[1], command=ShelfTabLayout.increase)
        cmds.menuItem(parent=popup, label='Shelf Line -', docTag=cls.MAIN_TAGS[2], command=ShelfTabLayout.decrease)
        cmds.menuItem(parent=popup, label='Shelf Line Reset', docTag=cls.MAIN_TAGS[3], command=ShelfTabLayout.reset)
