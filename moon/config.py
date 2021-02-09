# -*- coding: utf-8 -*-
from moon.join import pathjoin
import os


####################################################################################################
# 개발자 전용 상수
####################################################################################################
DEV_PATH = None
for drive in ['c:', 'd:']:
    dev_mvtools_path = pathjoin(drive, 'dev', 'moonlight')
    if os.path.isdir(dev_mvtools_path):
        DEV_PATH = pathjoin(drive, 'dev')


####################################################################################################
# 네트워크 드라이브 정의
####################################################################################################
# 인하우스툴
INHOUSETOOLS_DRIVE = 'x:'
if DEV_PATH:
    INHOUSETOOLS_DRIVE = DEV_PATH


####################################################################################################
# 인하우스툴 패스 정의
####################################################################################################
INHOUSETOOLS_PATH = pathjoin(INHOUSETOOLS_DRIVE, 'moonlight')
INHOUSETOOLS_LIB_PATH = pathjoin(INHOUSETOOLS_PATH, 'lib')
INHOUSETOOLS_ICON_PATH = pathjoin(INHOUSETOOLS_PATH, 'icons')
INHOUSETOOLS_MODULE_PATH = pathjoin(INHOUSETOOLS_PATH, 'modules')
INHOUSETOOLS_SCRIPT_PATH = pathjoin(INHOUSETOOLS_PATH, 'scripts')
INHOUSETOOLS_PLUGIN_PATH = pathjoin(INHOUSETOOLS_PATH, 'plugins')


####################################################################################################
# 테마
####################################################################################################
BACKGROUND_COLOR = 'ffba00'
