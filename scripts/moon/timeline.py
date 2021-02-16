# -*- coding: utf-8 -*-
import maya.cmds as cmds


FPS = {
    'game': 15,
    'film': 24,
    'pal': 25,
    'ntsc': 30,
    'show': 48,
    'palf': 50,
    'ntscf': 60,
    15: 'game',
    24: 'film',
    25: 'pal',
    30: 'ntsc',
    48: 'show',
    50: 'palf',
    60: 'ntscf',
}


def get_fps():
    unit = cmds.currentUnit(query=True, time=True)
    if unit.endswith('fps'):
        return int(unit[:-3])
    return FPS[unit]


def set_fps(val):
    if val in FPS:
        if isinstance(val, int):
            cmds.currentUnit(time=FPS[val])
        else:
            cmds.currentUnit(time=val)
