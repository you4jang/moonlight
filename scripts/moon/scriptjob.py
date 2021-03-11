# -*- coding: utf-8 -*-
import maya.cmds as cmds


def remove_script_job(package):
    """주어진 패키지와 관련된 스크립트 잡을 모두 지운다"""
    for sj in cmds.scriptJob(listJobs=True):
        buf = sj.split(':')
        if package in sj:
            cmds.scriptJob(kill=int(buf[0]), force=True)


def list_script_jobs():
    for job in cmds.scriptJob(listJobs=True):
        print(job.replace('\n', ''))
