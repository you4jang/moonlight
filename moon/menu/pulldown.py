# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from moon.join import crjoin
import random
import maya.cmds as cmds
import maya.mel as mel


_MAIN_MENU = 'Moonlight'


def create():
    if not cmds.menu(_MAIN_MENU, exists=True):
        maya_main_window = mel.eval('$gMainWindow = $gMainWindow')
        cmds.menu(
            _MAIN_MENU,
            parent=maya_main_window,
            label=_MAIN_MENU,
            tearOff=True,
            postMenuCommand=crjoin(
                'import moon.menu.pulldown',
                'reload(moon.menu.pulldown)',
                'moon.menu.pulldown.reload_items()',
            ),
        )


def reload_items(*_):
    if cmds.menu(_MAIN_MENU, exists=True):
        cmds.menu(_MAIN_MENU, edit=True, deleteAllItems=True)

    import moon.menu.pulldown_menu_set as menu
    reload(menu)

    _create_menuitem(menu.MENUS)


def _create_menuitem(menus, parent=_MAIN_MENU):
    for i, menu in enumerate(menus):
        kwargs = menu['kwargs']

        name = _get_menuitem_name(menu)

        if 'sub_menus' in menu:
            kwargs['subMenu'] = True
            kwargs['tearOff'] = True

        kwargs['parent'] = parent

        if 'image' in kwargs:
            kwargs['imageOverlayLabel'] = None

        var = ', '.join('%s=%r' % x for x in kwargs.iteritems())
        menuitem = eval('cmds.menuItem("{}", {})'.format(name, var))

        if 'sub_menus' in menu:
            _create_menuitem(menu['sub_menus'], parent=menuitem)


def _menuitem(name):
    return 'bean_menuitem_{}'.format(name).replace(' ', '_')


def _get_menuitem_name(menu):
    if 'name' in menu:
        return _menuitem(menu['name'])

    kwargs = menu['kwargs']

    if 'label' in kwargs:
        return _menuitem(kwargs['label'].strip().lower())
    elif 'divider' in kwargs:
        rand = str(int(random.random() * 1000)).zfill(4)
        name = 'divider{}'.format(rand)
        while cmds.menuItem(name, query=True, exists=True):
            rand = str(int(random.random() * 1000)).zfill(4)
            name = 'divider{}'.format(rand)
        return _menuitem(name)
