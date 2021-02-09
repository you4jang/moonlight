# -*- coding: utf-8 -*-
import pymel.core as pm
import moon.boot


# 경로 설정
# 인하우스툴과 인하우스툴의 하위에 있는 모듈이나 폴더를 읽기 위해서 미리 메모리에 로드한다
moon.boot.init_paths()


# GUI 모드에서만 작동하도록 한다
if not pm.about(batch=True):

    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # 빠른 마야 종료
    import moon.mayaexit
    moon.mayaexit.setup()

    # 풀다운메뉴
    pm.evalDeferred(moon.boot.customize_pulldown_menu)
    pm.evalDeferred(moon.boot.init_preferences)
