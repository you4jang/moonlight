# -*- coding: utf-8 -*-
from __future__ import unicode_literals


if 'active' not in globals().keys():
    active = {}


def exist(key):
    if not key:
        return False
    return key in active


def add(key, value):
    if not key or not value:
        return False
    active[key] = value
    return True


def delete(key):
    if not key:
        return False
    if not exist(key):
        return False
    del active[key]


def get(key):
    if not key:
        return
    if not exist(key):
        return
    return active[key]


def keys():
    return active.keys()


def show():
    print('active keys :', keys())
