# -*- coding: utf-8 -*-
from moon.qt import infobox
import maya.cmds as cmds
import pymel.core as pm


def unknown(delete=False):
    unknowns = []
    for node in pm.ls(type=('unknown', 'unknownDag', 'unknownTransform')):
        unknowns.append(node.name())
        if not node.objExists():
            continue
        pm.lockNode(node, lock=False)
        if delete:
            pm.delete(node)
    
    return unknowns


def unused_constraints(delete=False):
    types = [
        "pointConstraint",
        "pointOnPolyConstraint",
        "aimConstraint",
        "orientConstraint",
        "parentConstraint",
        "scaleConstraint",
        "normalConstraint",
        "tangentConstraint",
        "geometryConstraint"
    ]
    const = cmds.ls(type=types)
    if not const:
        return

    unused = []

    for c in const:
        dests = cmds.listConnections(c, source=False, destination=True)
        if dests:
            outgoing = False
            for d in dests:
                if d != c:
                    outgoing = True
            if not outgoing:
                unused.append(c)
        else:
            unused.append(c)

    if delete:
        cmds.delete(unused)

    return unused


def unused_expressions(delete=False):
    expressions = pm.ls(type='expression')
    if not expressions:
        return

    unused = []

    for e in expressions:
        if not cmds.listConnections(e + '.output', source=False, destination=True, skipConversionNodes=True):
            unused.append(e)

    if delete:
        cmds.delete(unused)

    return unused


def unused_plugins(dialog=False):
    plugins = pm.unknownPlugin(query=True, list=True)
    if plugins:
        for un in plugins:
            try:
                pm.unknownPlugin(un, remove=True)
            except:
                pass
    if dialog:
        infobox('사용하지 않는 플러그인을 모두 제거하였습니다.')


def set_soften_edges_all():
    for sh in cmds.ls(type='mesh', noIntermediate=True):
        cmds.polySoftEdge(sh, angle=180, constructionHistory=False)
        cmds.delete(sh, constructionHistory=True)


def set_harden_edges_all():
    for sh in cmds.ls(type='mesh', noIntermediate=True):
        cmds.polySoftEdge(sh, angle=0, constructionHistory=False)
        cmds.delete(sh, constructionHistory=True)


def reset_display_smoothness():
    for top in pm.ls(assemblies=True, type='transform'):
        try:
            pm.displaySmoothness(top, polygonObject=0)
        except:
            pass


def remove_chinese_vaccine():
    pass
