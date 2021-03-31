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
                    'label': 'ksd6 - EDL Editor',
                    'image': 'ksd6/edl_editor.png',
                    'command': crjoin(
                        'import moon.ksd6.edl_editor',
                        'reload(moon.ksd6.edl_editor)',
                        'moon.ksd6.edl_editor.main()',
                    ),
                },
            },
            {
                'kwargs': {
                    'label': 'ksd6 - Lighting Scene Manager',
                    'image': 'ksd6/lighting_scene_manager.png',
                    'command': crjoin(
                        'import moon.ksd6.lighting_scene_manager',
                        'reload(moon.ksd6.lighting_scene_manager)',
                        'moon.ksd6.lighting_scene_manager.main()',
                    ),
                },
            },
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
    # {
    #     'kwargs': {
    #         'label': 'Follow Cam',
    #         'image': 'follow_cam.bmp',
    #         'command': crjoin(
    #             'import moon.apps.followcam',
    #             'reload(moon.apps.followcam)',
    #             'moon.apps.followcam.create()',
    #         ),
    #     },
    # },
    # {
    #     'kwargs': {
    #         'label': 'Imageplane Tools',
    #         'image': 'imageplane_tools.png',
    #         'command': crjoin(
    #             'import moon.apps.imageplane_tools',
    #             'reload(moon.apps.imageplane_tools)',
    #             'moon.apps.imageplane_tools.window()',
    #         ),
    #     },
    # },
]
