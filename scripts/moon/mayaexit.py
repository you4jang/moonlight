# -*- coding: utf-8 -*-
import maya.cmds as cmds


def setup():
    cmds.evalDeferred("import maya.mel as mel")
    cmds.evalDeferred("mel.eval('source \"superexit.mel\"')")
