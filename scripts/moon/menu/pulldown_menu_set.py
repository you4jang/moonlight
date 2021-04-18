# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from moon.join import crjoin


MENUS = [
    ####################################################################################################
    # 필수 앱
    ####################################################################################################
    {
        'kwargs': {
            'divider': True,
            'dividerLabel': 'Main',
        },
    },
    {
        'kwargs': {
            'label': 'moon Login',
            'image': 'login.jpg',
            'command': crjoin(
                'import moon.authentication',
                'reload(moon.authentication)',
                'moon.authentication.show_window()',
            ),
        },
    },
    {
        'kwargs': {
            'label': 'Match Transform',
            'image': 'match_transform.bmp',
            'command': crjoin(
                'import moon.manip',
                'reload(moon.manip)',
                'moon.manip.match_transform()',
            ),
        },
    },
    {
        'kwargs': {
            'label': 'Match Position',
            'image': 'match_position.bmp',
            'command': crjoin(
                'import moon.manip',
                'reload(moon.manip)',
                'moon.manip.match_position()',
            ),
        },
    },
    {
        'kwargs': {
            'label': 'Match Scale',
            'image': 'match_scale.bmp',
            'command': crjoin(
                'import moon.manip',
                'reload(moon.manip)',
                'moon.manip.match_scale()',
            ),
        },
    },
    ####################################################################################################
    # 프로젝트
    ####################################################################################################
    {
        'kwargs': {
            'divider': True,
            'dividerLabel': 'Projects',
        },
    },
    {
        'kwargs': {
            'label': 'ksd6',
        },
        'sub_menus': [
            {
                'kwargs': {
                    'label': 'ksd6 - Shotgun Uploader',
                    'image': 'ksd6/shotgun_uploader.png',
                    'command': crjoin(
                        'import moon.ksd6.shotgun_uploader',
                        'reload(moon.ksd6.shotgun_uploader)',
                        'moon.ksd6.shotgun_uploader.main()',
                    ),
                },
            },
        ],
    },
    ####################################################################################################
    # 공통
    ####################################################################################################
    {
        'kwargs': {
            'divider': True,
            'dividerLabel': 'Common',
        },
    },
    {
        'kwargs': {
            'label': 'Lighting Scene Manager',
            'image': 'ksd6/lighting_scene_manager.png',
            'command': crjoin(
                'import moon.apps.lighting_scene_manager',
                'reload(moon.apps.lighting_scene_manager)',
                'moon.apps.lighting_scene_manager.main()',
            ),
        },
    },
    {
        'kwargs': {
            'label': 'EDL Editor',
            'command': crjoin(
                'import moon.apps.edl_editor',
                'reload(moon.apps.edl_editor)',
                'moon.apps.edl_editor.main()',
            ),
        },
    },
    ####################################################################################################
    # 카메라
    ####################################################################################################
    {
        'kwargs': {
            'divider': True,
            'dividerLabel': 'Camera',
        },
    },
    {
        'kwargs': {
            'label': 'Camera View Manager',
            'image': 'camviewmgr.bmp',
            'command': crjoin(
                'import moon.cam.camviewmgr',
                'reload(moon.cam.camviewmgr)',
                'moon.cam.camviewmgr.main()',
            ),
        },
    },
]
