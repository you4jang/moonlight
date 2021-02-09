# -*- coding: utf-8 -*-
import os


def pathjoin(*args, **kwargs):
    if 'osjoin' in kwargs:
        if kwargs['osjoin']:
            return os.sep.join(*args)
    return '/'.join(args)


def namejoin(*args):
    return '_'.join(args)


def uujoin(*args):
    return '__'.join(args)


def attrjoin(*args):
    return '.'.join(args)


def crjoin(*args):
    return '\n'.join(args)


def spjoin(*args):
    return ' '.join(args)


def wordjoin(*args):
    return ''.join(args)


def subjoin(*args):
    return '-'.join(args)
