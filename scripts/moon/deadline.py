# -*- coding: utf-8 -*-
from moon.path import dirs
from moon.join import pathjoin
import os
import uuid
import subprocess
import maya.mel as mel


def load_deadline():
    deadline = 'z:/DeadlineRepository10/submission/Maya/Client/DeadlineMayaClient.mel'
    if os.path.exists(deadline):
        mel.eval('source "{}"'.format(deadline))


class Info(object):
    """
    데드라인에서 제공해주는 Deadline Command 유틸리티를 이용해 데드라인에 렌더링 잡을 등록할 때 사용하는 Plugin Info 파일을
    생성하고, 관련 옵션들을 집어넣거나 삭제할 수 있는 클래스.
    """
    
    def __init__(self, filename=None):
        """
        파일이름은 선택사항으로, 지정하지 않을 경우 임시폴더의 임시파일이름으로 생성해준다.
        """
        # job info 파일의 파일이름을 정의한다.
        self.path = dirs(os.path.dirname(filename)) if filename else os.environ['temp']
        self.filename = filename if filename else self.path + os.sep + str(uuid.uuid4()) + '.' + 'txt'
        # 각종 옵션을 저장할 사전을 만들어놓는다.
        self.options = {}
        # 옵션을 저장할 변수는 사전형이기 때문에, 나중에 파일을 만들 경우 원하는 순서대로 옵션을 파일에 추가할 수 없다.
        # 따라서, 옵션의 키를 순서대로 만들기 위해 리스트도 하나 만들어놓는다.
        self.key_order = []

    def add(self, key, value):
        """키와 값을 가진 쌍의 옵션을 생성한다."""
        if key not in self.key_order:
            self.key_order.append(key)
        self.options[key] = value

    def delete(self, key):
        """지정한 키와 관련된 데이터들을 삭제한다."""
        count = self.key_order.count(key)
        if count > 0:
            index = self.key_order.index(key)
            del self.key_order[index]
        if key in self.options:
            del self.options[key]

    def create(self):
        """옵션을 이용하여 파일을 생성한다."""
        with file(self.filename, 'w') as f:
            for key in self.key_order:
                f.write(key + '=' + self.options[key] + '\n')
        return self.filename


class JobInfo(Info):
    """
    Deadline에서 제공해주는 Deadline Command 유틸리티를 이용해 데드라인에 렌더링 잡을 등록할 때 사용하는 Job Info 파일을 생성
    하고, 관련 옵션들을 집어넣거나 삭제할 수 있는 클래스. 대부분의 기능이 PluginInfo 클래스와 비슷하므로 상속받아 사용한다. 필수
    옵션이 있기 때문에 생성자에서 필수옵션을 추가해준다.
    """
    
    def __init__(self, plugin, filename=None):
        """
        플러그인은 job info 파일의 필수옵션이므로, 반드시 지정하도록 해야한다.
        파일이름은 선택사항으로, 지정하지 않을 경우 임시폴더의 임시파일이름으로 생성해준다.
        """
        super(JobInfo, self).__init__(filename)
        # 지정된 플러그인이 유효한지 알아보고, 유효하면 변수에 저장한다.
        self.plugin = plugin
        # 필수 옵션을 지정해놓는다.
        self.add('Plugin', plugin)


class PluginInfo(Info):
    """
    Deadline에서 제공해주는 Deadline Command 유틸리티를 이용해 데드라인에 렌더링 잡을 등록할 때 사용하는 Job Info 파일을 생성
    하고, 관련 옵션들을 집어넣거나 삭제할 수 있는 클래스. 대부분의 기능이 PluginInfo 클래스와 비슷하므로 상속받아 사용한다. 필수
    옵션이 있기 때문에 생성자에서 필수옵션을 추가해준다.
    """

    def __init__(self, filename=None):
        """
        플러그인은 job info 파일의 필수옵션이므로, 반드시 지정하도록 해야한다.
        파일이름은 선택사항으로, 지정하지 않을 경우 임시폴더의 임시파일이름으로 생성해준다.
        """
        super(PluginInfo, self).__init__(filename)


class Submission(object):
    """
    Deadline에서 제공해주는 Deadline Command 유틸리티를 이용해 데드라인에 렌더링 잡을 등록하기 위한 클래스.
    """
    
    DEADLINE_PATH = None
    DEADLINE_COMMAND = None
    
    if 'DEADLINE_PATH' in os.environ:
        DEADLINE_PATH = os.environ['DEADLINE_PATH']
        DEADLINE_COMMAND = DEADLINE_PATH + os.sep + 'deadlinecommand.exe'
    
    def __init__(self, job_info, plugin_info, scene_filename=None):
        self.job_info = job_info
        self.plugin_info = plugin_info
        self.scene_filename = scene_filename.replace('/', os.sep)
        
    def submit(self):
        """2개의 필수 파일을 이용하여 데드라인에 잡을 등록한다."""
        if not self.DEADLINE_PATH or not self.DEADLINE_COMMAND:
            print 'The system environment, DEADLINE_PATH, has not set.'
            return
        
        if not self.job_info or not self.plugin_info:
            print 'job_info or plugin_info file is not specified.'
            return
        
        job_filename = pathjoin(dirs(os.environ['temp']), str(uuid.uuid4()) + '.txt', sep=os.sep)
        plugin_filename = pathjoin(dirs(os.environ['temp']), str(uuid.uuid4()) + '.txt', sep=os.sep)
        
        self.create_file(self.job_info, job_filename)
        self.create_file(self.plugin_info, plugin_filename)
        
        cmd = [
            self.DEADLINE_COMMAND,
            job_filename,
            plugin_filename,
        ]
        print job_filename
        print plugin_filename
        # print '"' + '" "'.join(cmd) + '"'
        
        if self.scene_filename:
            cmd.append(self.scene_filename)

        result = subprocess.check_output(cmd, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        data = {}
        for res in result.split('\r\n'):
            temp = res.split('=')
            if len(temp) == 2:
                data[temp[0]] = temp[1]
        return data

    @staticmethod
    def create_file(data, filename):
        with file(filename, 'w') as f:
            for k, v in data.options.items():
                if isinstance(v, bool):
                    v = '1' if v else '0'
                f.write('{}={}\n'.format(k, v))
