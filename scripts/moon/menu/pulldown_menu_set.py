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
                    'label': 'ksd6 - Lighting Scene Manager',
                    'image': 'ksd6/lighting_scene_manager.png',
                    'command': crjoin(
                        'import moon.ksd6.lighting_scene_manager',
                        'reload(moon.ksd6.lighting_scene_manager)',
                        'moon.ksd6.lighting_scene_manager.main()',
                    ),
                },
            },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Heads Up Display',
    #                 'image': 'cc/hud.jpg',
    #                 'command': crjoin(
    #                     'import moon.cc.hud',
    #                     'reload(moon.cc.hud)',
    #                     'moon.cc.hud.main()',
    #                 ),
    #             },
    #         },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Playblast Manager',
    #                 'image': 'video-player.png',
    #                 'command': crjoin(
    #                     'import moon.cc.playblast_manager',
    #                     'reload(moon.cc.playblast_manager)',
    #                     'moon.cc.playblast_manager.main()',
    #                 ),
    #             },
    #         },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Asset Loader',
    #                 'image': 'cc/asset_loader.jpg',
    #                 'command': crjoin(
    #                     'import moon.cc.asset_loader',
    #                     'reload(moon.cc.asset_loader)',
    #                     'moon.cc.asset_loader.main()',
    #                 ),
    #             },
    #         },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Camera Baking',
    #                 'image': 'cc/camera_baking.png',
    #                 'command': crjoin(
    #                     'import moon.cc.cam_bake',
    #                     'reload(moon.cc.cam_bake)',
    #                     'moon.cc.cam_bake.bake()',
    #                 ),
    #             },
    #         },
        ],
    },
    ####################################################################################################
    # 카메라
    ####################################################################################################
    # {
    #     'kwargs': {
    #         'divider': True,
    #         'dividerLabel': 'Camera',
    #     },
    # },
    # {
    #     'kwargs': {
    #         'label': 'Camera View Manager',
    #         'image': 'camviewmgr.bmp',
    #         'command': crjoin(
    #             'import moon.apps.camviewmgr',
    #             'reload(moon.apps.camviewmgr)',
    #             'moon.apps.camviewmgr.main()',
    #         ),
    #     },
    # },
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
