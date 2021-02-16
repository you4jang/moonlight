# -*- coding: utf-8 -*-
import os
import logging


LOG_LEVEL = logging.INFO


if 'dev' in os.environ and os.environ['dev'] == 'true':
    LOG_LEVEL = logging.DEBUG


def get_logger(name, log_level=None, filename=None):
    # 로거에 정의할 이름. 주로 해당 클래스나 모듈 이름.
    log = logging.getLogger(name)
    log.handlers = []
    
    ####################################################################################################
    # 포매터 정의
    ####################################################################################################
    formatter = logging.Formatter('%(asctime)s %(levelname)5s [%(name)s:%(lineno)5d] %(message)s')
    
    ####################################################################################################
    # 콘솔 핸들러 정의
    ####################################################################################################
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    
    ####################################################################################################
    # 파일 핸들러 정의
    ####################################################################################################
    if filename:
        path = os.path.dirname(filename)
        if not os.path.isdir(path):
            os.makedirs(path)
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    
    # 마야 로거에 확산되는 것을 막는다.
    log.propagate = 0
    
    if log_level:
        if log_level == 'info':
            log.setLevel(logging.INFO)
        elif log_level == 'debug':
            log.setLevel(logging.DEBUG)
        elif log_level == 'critical':
            log.setLevel(logging.CRITICAL)
        elif log_level == 'error':
            log.setLevel(logging.ERROR)
    else:
        log.setLevel(LOG_LEVEL)

    return log
