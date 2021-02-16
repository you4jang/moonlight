# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from bean.join import crjoin


MENUS = [
    {
        'kwargs': {
            'divider': True,
            'dividerLabel': 'Projects',
        },
    },
    # {
    #     'kwargs': {
    #         'label': 'Project CC',
    #     },
    #     'sub_menus': [
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Animation Scene Manager',
    #                 'image': 'cc/animation_scene_manager.jpg',
    #                 'command': crjoin(
    #                     'import bean.cc.animation_scene_manager',
    #                     'reload(bean.cc.animation_scene_manager)',
    #                     'bean.cc.animation_scene_manager.main()',
    #                 ),
    #             },
    #         },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Heads Up Display',
    #                 'image': 'cc/hud.jpg',
    #                 'command': crjoin(
    #                     'import bean.cc.hud',
    #                     'reload(bean.cc.hud)',
    #                     'bean.cc.hud.main()',
    #                 ),
    #             },
    #         },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Playblast Manager',
    #                 'image': 'video-player.png',
    #                 'command': crjoin(
    #                     'import bean.cc.playblast_manager',
    #                     'reload(bean.cc.playblast_manager)',
    #                     'bean.cc.playblast_manager.main()',
    #                 ),
    #             },
    #         },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Asset Loader',
    #                 'image': 'cc/asset_loader.jpg',
    #                 'command': crjoin(
    #                     'import bean.cc.asset_loader',
    #                     'reload(bean.cc.asset_loader)',
    #                     'bean.cc.asset_loader.main()',
    #                 ),
    #             },
    #         },
    #         {
    #             'kwargs': {
    #                 'label': 'CC - Camera Baking',
    #                 'image': 'cc/camera_baking.png',
    #                 'command': crjoin(
    #                     'import bean.cc.cam_bake',
    #                     'reload(bean.cc.cam_bake)',
    #                     'bean.cc.cam_bake.bake()',
    #                 ),
    #             },
    #         },
    #     ],
    # },
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
    #             'import bean.apps.camviewmgr',
    #             'reload(bean.apps.camviewmgr)',
    #             'bean.apps.camviewmgr.main()',
    #         ),
    #     },
    # },
    # {
    #     'kwargs': {
    #         'label': 'Follow Cam',
    #         'image': 'follow_cam.bmp',
    #         'command': crjoin(
    #             'import bean.apps.followcam',
    #             'reload(bean.apps.followcam)',
    #             'bean.apps.followcam.create()',
    #         ),
    #     },
    # },
    # {
    #     'kwargs': {
    #         'label': 'Imageplane Tools',
    #         'image': 'imageplane_tools.png',
    #         'command': crjoin(
    #             'import bean.apps.imageplane_tools',
    #             'reload(bean.apps.imageplane_tools)',
    #             'bean.apps.imageplane_tools.window()',
    #         ),
    #     },
    # },
]
