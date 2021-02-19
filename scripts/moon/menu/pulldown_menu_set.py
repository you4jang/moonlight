# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from moon.join import crjoin


MENUS = [
    {
        'kwargs': {
            'divider': True,
            'dividerLabel': 'Projects',
        },
    },
    {
        'kwargs': {
            'label': 'Kong7',
        },
        'sub_menus': [
            {
                'kwargs': {
                    'label': 'Kong7 - EDL Editor',
                    'image': 'kong7/edl_editor.png',
                    'command': crjoin(
                        'import prj.kong7.edl_editor',
                        'reload(prj.kong7.edl_editor)',
                        'prj.kong7.edl_editor.main()',
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
