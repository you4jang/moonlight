# -*- coding: utf-8 -*-
from moon.join import pathjoin


####################################################################################################
# 샷건 관련
####################################################################################################
SG_PROJECT = {'type': 'Project', 'id': 122}

SG_STEP_ANIMATION = {'type': 'Step', 'id': 106}
SG_STEP_FX = {'type': 'Step', 'id': 6}
SG_STEP_LIGHTING = {'type': 'Step', 'id': 7}


####################################################################################################
# 파일 경로 관련
####################################################################################################
SV_PRJ_PATH = pathjoin('K:', 'KongsuniDance6')
SV_THUMBNAIL_PATH = pathjoin(SV_PRJ_PATH, 'thumbnails')
SV_ANI_PATH = pathjoin(SV_PRJ_PATH, '03_Animation', '02_Scenes')
SV_LGT_PATH = pathjoin(SV_PRJ_PATH, '04_LRComp', '01_Lighting')
