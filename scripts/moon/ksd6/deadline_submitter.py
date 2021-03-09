# -*- coding: utf-8 -*-
from moon.authentication import *
from moon.path import *
from moon.qt import *
import os
import re
import shutil
import subprocess
import maya.cmds as cmds
import pymel.core as pm
import moon.deadline
reload(moon.deadline)
import moon.scriptjob
import moon.ksd6.config as config
reload(config)


class DeadlineSubmitterWindow(MainDialog):

    LABEL_WIDTH = 135

    SUSPENDED_JOB = False
    PRIORITY = '50'
    MACHINE_LIMIT = '0'
    CHUNK_SIZE = '5'
    CONCURRENT_TASK = '1'
    GPU_PER_TASK = '0'

    def __init__(self, parent=maya_widget()):
        self.win = 'deadline_submitter_window'
        super(DeadlineSubmitterWindow, self).__init__(self.win, parent)
        self.parent = parent
        self.ui()

    def ui(self):
        self.setWindowTitle('ksd6 - Deadline Submitter')

        self.window_layout = QVBoxLayout(self)
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(0)
        self.window_layout.setAlignment(Qt.AlignTop)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(9, 9, 9, 9)
        self.main_layout.setSpacing(6)

        self.main_scroll = QScrollArea()
        self.main_scroll.setFrameShape(QFrame.NoFrame)
        self.main_scroll.setFrameShadow(QFrame.Plain)
        self.main_scroll.setWidgetResizable(True)
        self.main_scroll.setWidget(QGroupBox())

        self.main_scroll_layout = QVBoxLayout(self.main_scroll.widget())
        self.main_scroll_layout.setContentsMargins(9, 9, 9, 9)

        self.main_form_layout = QFormLayout()
        self.main_form_layout.setContentsMargins(0, 0, 0, 0)
        self.main_form_layout.setSpacing(4)

        self.job_name_field = QLineEdit()
        self.job_name_field.setFixedWidth(150)

        self.comment_field = QLineEdit()
        self.suspended_checkbox = QCheckBox('Submit As Suspend')
        self.suspended_checkbox.setChecked(self.SUSPENDED_JOB)

        self.pool_combo = Combobox(korean=False)
        self.pool_combo.setMinimumSize(100, 22)

        self.sec_pool_combo = Combobox(korean=False)
        self.sec_pool_combo.setMinimumSize(100, 22)

        self.group_combo = Combobox(korean=False)
        self.group_combo.setMinimumSize(100, 22)

        self.priority_field = QLineEdit()
        self.priority_field.setText(self.PRIORITY)
        self.priority_field.setFixedWidth(50)

        self.limit_machine_field = QLineEdit()
        self.limit_machine_field.setFixedWidth(50)
        self.limit_machine_field.setText(self.MACHINE_LIMIT)

        self.chunk_size_field = QLineEdit()
        self.chunk_size_field.setFixedWidth(50)
        self.chunk_size_field.setText(self.CHUNK_SIZE)

        self.concurrent_task_field = QLineEdit()
        self.concurrent_task_field.setFixedWidth(50)
        self.concurrent_task_field.setText(self.CONCURRENT_TASK)

        self.gpu_per_task_field = QLineEdit()
        self.gpu_per_task_field.setFixedWidth(50)
        self.gpu_per_task_field.setText(self.GPU_PER_TASK)

        self.frame_range_layout = QHBoxLayout()
        self.frame_range_layout.setSpacing(1)
        self.start_frame_field = QLineEdit()
        self.start_frame_field.setFixedWidth(50)
        self.end_frame_field = QLineEdit()
        self.end_frame_field.setFixedWidth(50)
        self.frame_range_layout.addWidget(self.start_frame_field)
        self.frame_range_layout.addWidget(QLabel(' ~ '))
        self.frame_range_layout.addWidget(self.end_frame_field)
        self.frame_range_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.camera_combo = Combobox(korean=False)
        self.camera_combo.setMinimumSize(200, 22)

        self.render_layer_checkbox = QCheckBox('Using Render Layers')
        self.render_layer_checkbox.toggled.connect(self.on_using_render_layer_checkbox_changed)

        self.project_path_field = QLineEdit()
        self.project_path_field.setFixedHeight(22)

        self.output_field = QLineEdit()
        self.output_field.setFixedHeight(22)

        self.individual_render_layer_widget = IndividualRenderLayerTable(parent=self)
        self.individual_render_layer_widget.setEnabled(False)

        indi_layout = QHBoxLayout()

        self.add_indi_btn = Button('Add Layer', korean=False)
        self.add_indi_btn.setMinimumSize(80, 22)
        self.add_indi_btn.clicked.connect(self.add_individual_layer_setting)

        self.init_width_btn = IconButton('width.png', 23, 13)
        self.init_width_btn.clicked.connect(self.individual_render_layer_widget.init_cell_widths)

        indi_layout.addWidget(self.add_indi_btn)
        indi_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        indi_layout.addWidget(self.init_width_btn)

        self.main_form_layout.addRow(QLabel('Job Name'), self.job_name_field)
        self.main_form_layout.addRow(QLabel('Frames'), self.frame_range_layout)
        self.main_form_layout.addRow(hline())
        # self.deadline_job_layout.addRow(QLabel('Cam'), self.camera_combo)
        # self.deadline_job_layout.addRow(QLabel('Comment'), self.comment_field)
        self.main_form_layout.addRow(None, self.suspended_checkbox)
        self.main_form_layout.addRow(QLabel('Project Path'), self.project_path_field)
        self.main_form_layout.addRow(QLabel('Output Path'), self.output_field)
        self.main_form_layout.addRow(hline())
        self.main_form_layout.addRow(None, self.render_layer_checkbox)
        self.main_form_layout.addRow(QLabel('Pool'), self.pool_combo)
        self.main_form_layout.addRow(QLabel('Secodary Pool'), self.sec_pool_combo)
        self.main_form_layout.addRow(QLabel('Group'), self.group_combo)
        self.main_form_layout.addRow(hline())
        self.main_form_layout.addRow(QLabel('Priority'), self.priority_field)
        self.main_form_layout.addRow(QLabel('Machine Limit'), self.limit_machine_field)
        self.main_form_layout.addRow(hline())
        self.main_form_layout.addRow(QLabel('Concurrent Task'), self.concurrent_task_field)
        self.main_form_layout.addRow(QLabel('Frame Per Task'), self.chunk_size_field)
        self.main_form_layout.addRow(QLabel('GPUs Per Task'), self.gpu_per_task_field)
        self.main_form_layout.addRow(hline())
        self.main_form_layout.addRow(QLabel('Individual Render Layer'), indi_layout)

        ####################################################################################################
        # 전송 버튼 관련
        ####################################################################################################
        self.submit_button = QPushButton('Submit')
        self.submit_button.setFixedHeight(30)
        self.submit_button.setIcon(QIcon(img_path('submit.png')))
        self.submit_button.clicked.connect(self.submit_to_deadline)

        ####################################################################################################
        # 레이아웃
        ####################################################################################################
        self.main_scroll_layout.addLayout(self.main_form_layout)
        self.main_scroll_layout.addWidget(self.individual_render_layer_widget)

        self.main_layout.addWidget(self.main_scroll)
        self.main_layout.addWidget(self.submit_button)
        self.window_layout.addLayout(self.main_layout)

        if self.parent == maya_widget():
            restore_window(self)
        self.setFocus()

        ####################################################################################################
        # 스타트업
        ####################################################################################################
        self.init_pools()
        self.initialize_scene()

    def on_using_render_layer_checkbox_changed(self, state):
        self.add_indi_btn.setEnabled(state)
        self.init_width_btn.setEnabled(state)
        self.individual_render_layer_widget.setEnabled(state)

    def add_individual_layer_setting(self):
        win = IndividualRenderLayerSettingCreateWindow(parent=self)
        result = win.exec_()
        if result:
            self.individual_render_layer_widget.add(win.get_data())

    def init_pools(self):
        self.pools = []
        self.groups = []

        # 데드라인 커맨드를 이용해 풀, 세컨더리 풀, 그룹을 읽어온다.
        for pool in self.get_deadline_pools():
            self.pools.append(pool)

        for grp in self.get_deadline_groups():
            self.groups.append(grp)

    def initialize_scene(self):
        """현재 열려있는 씬을 토대로 정보를 추출하여 각 필드의 초기값을 만든다"""
        cur = cmds.file(query=True, sceneName=True, shortName=True)
        if not cur:
            return

        # 파일의 이름은 씬 파일의 이름과 같으므로 이것을 데드라인 잡의 이름으로 지정한다.
        self.job_name_field.setText(basenameex(cur))

        # 시작프레임과 끝프레임을 파악하여 프레임 범위의 필드에 입력한다.
        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)
        self.start_frame_field.setText(str(int(start_frame)))
        self.end_frame_field.setText(str(int(end_frame)))

        # 씬 안에 존재하는 모든 카메라를 찾아,
        # 그 중 렌더링가능 속성이 켜져있는 카메라만 카메라 콤보박스에 추가한다.
        for cam in pm.ls(type='camera'):
            renderable = cam.renderable.get()
            if renderable:
                self.camera_combo.addItem(cam.name())

        for pool in self.pools:
            self.pool_combo.addItem(pool)
            self.sec_pool_combo.addItem(pool)

        for grp in self.groups:
            self.group_combo.addItem(grp)

        # 씬 안에 렌더레이어가 있을 경우 렌더레이어를 사용하여 렌더링 걸 수 있도록 옵션을 켜놓는다.
        render_layers = []
        for layer in pm.ls(type='renderLayer'):
            # 디폴트 렌더 레이어는 패스한다.
            if layer.name().endswith('defaultRenderLayer'):
                continue
            render_layers.append(layer)
        if len(render_layers) > 0:
            self.render_layer_checkbox.setChecked(True)

        # 시퀀스 저장 경로 지정
        buf = basenameex(cur).split('_')
        ep = buf[0]
        cut = buf[1]
        path = pathjoin(config.SV_REN_PATH, ep, cut)
        self.project_path_field.setText(path)
        self.output_field.setText(path)

    @staticmethod
    def get_project_code():
        current_scene_file = cmds.file(query=True, sceneName=True)
        if not current_scene_file or current_scene_file == '':
            return

        path = os.path.dirname(current_scene_file)

        # 경로를 분리하여 이것이 wms 작업파일인지 판단하고,
        # wms 작업파일이 맞다면 미리 지정해놓은 프로젝트 코드의 자리에서 프로젝트 코드를 확인한다.
        buf = path.split('/')
        if buf[1] == 'wms' and buf[2] == 'pipeline' and buf[3] == 'work':
            return buf[4]

    def get_frame_range(self):
        start_frame = self.start_frame_field.text()
        end_frame = self.end_frame_field.text()
        return '{}-{}'.format(start_frame, end_frame)

    def submit_to_deadline(self):
        local_scene_file = cmds.file(query=True, sceneName=True)
        server_scene_file = 'r' + local_scene_file[1:]

        server_root_path = dirs(os.path.dirname(server_scene_file))
        server_tex_path = dirs(pathjoin(server_root_path, 'texture'))

        ####################################################################################################
        # 텍스쳐 파일 정리
        ####################################################################################################
        unknown_tex_nodes = []
        unknown_rs_tex_nodes = []

        for tex in pm.ls(type='file'):
            tex_file = tex.fileTextureName.get()
            if not tex_file or tex_file.strip() == '':
                unknown_tex_nodes.append(tex)
                continue
            regex = re.match('r:', tex_file, re.IGNORECASE)
            if not regex:
                unknown_tex_nodes.append(tex)

        for tex in pm.ls(type=('RedshiftNormalMap', 'RedshiftSprite')):
            tex_file = tex.tex0.get()
            if not tex_file or tex_file.strip() == '':
                unknown_rs_tex_nodes.append(tex_file)
                continue
            regex = re.match('r:', tex_file, re.IGNORECASE)
            if not regex:
                unknown_rs_tex_nodes.append(tex)

        ####################################################################################################
        # 레퍼런스 정리
        ####################################################################################################
        for ref in pm.ls(type='reference'):
            try:
                filename = ref.fileName(True, False, False)
            except:
                continue
            if filename.lower().startswith('d:'):
                new_filename = 'r:' + filename[2:]
                # R 서버에 파일이 존재하지 않는다면 파일을 복사한다.
                if not os.path.isfile(new_filename):
                    dirs(os.path.dirname(new_filename))
                    shutil.copy2(filename, new_filename)
                r = pm.FileReference(ref)
                r.load(new_filename)

        # 파일을 저장하기 직전 반드시 마스터 렌더 레이어로 이동한 후 저장하도록 한다.
        pm.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')

        ####################################################################################################
        # 파일 강제 저장
        ####################################################################################################
        if cmds.file(query=True, modified=True):
            cmds.file(force=True, save=True)

        ####################################################################################################
        # 마야 씬 익스포트
        ####################################################################################################
        cmds.file(
            server_scene_file,
            force=True,
            options='v=0;',
            type='mayaBinary',
            preserveReferences=True,
            exportAll=True,
        )

        ####################################################################################################
        # 아웃풋 경로 생성
        ####################################################################################################
        output_path = dirs(self.output_field.text())

        ####################################################################################################
        # 로그인 쿠키
        ####################################################################################################
        cookie = MoonLoginCookie.get_login_user()

        ####################################################################################################
        # 주어진 데이터를 이용하여 데드라인에 잡을 생성한다.
        ####################################################################################################
        priority = self.priority_field.text()
        pool = self.pool_combo.currentText()
        sec_pool = self.sec_pool_combo.currentText()
        group = self.group_combo.currentText()
        concurrent_task = self.concurrent_task_field.text()
        frame_per_task = self.chunk_size_field.text()
        gpus_per_task = self.gpu_per_task_field.text()

        if self.render_layer_checkbox.isChecked():
            individual_set = self.individual_render_layer_widget.get_data()
        else:
            individual_set = {}

        job = moon.deadline.JobInfo('MayaBatch')
        job.add('Name', self.job_name_field.text())
        job.add('Comment', self.comment_field.text())
        job.add('Frames', self.get_frame_range())
        job.add('UserName', cookie.name.encode('euc-kr'))
        job.add('Department', cookie.team)
        job.add('ChunkSize', frame_per_task)
        job.add('Pool', pool)
        job.add('SecondaryPool', sec_pool)
        job.add('Group', group)
        job.add('Priority', priority)
        job.add('MachineLimit', self.limit_machine_field.text())
        job.add('ConcurrentTasks', concurrent_task)
        job.add('OutputDirectory0', output_path)
        # job.add('Pool', 'maya')
        # job.add('Protected', 'true')
        # job.add('MinRenderTimeSeconds', '5')
        # job.add('TaskTimeoutMinutes', '180')
        # job.add('EnableAutoTimeout', 'true')

        if self.suspended_checkbox.isChecked():
            job.add('InitialStatus', 'Suspended')

        plugin = moon.deadline.PluginInfo()
        plugin.add('SceneFile', server_scene_file)
        plugin.add('Camera', self.camera_combo.currentText())
        plugin.add('ProjectPath', pathjoin('r:/wms/pipeline/work', self.get_project_code()))
        plugin.add('OutputFilePath', output_path)
        plugin.add('Renderer', 'vray')
        plugin.add('Version', cmds.about(version=True))
        plugin.add('Build', '64bit')
        plugin.add('StrictErrorChecking', True)
        plugin.add('GPUsPerTask', gpus_per_task)
        plugin.add('RedshiftVerbose', '2')
        # plugin.add('LocalRendering', 'true')
        # plugin.add('Width', '1920')
        # plugin.add('Height', '1080')
        # plugin.add('RenderLayer', data['layer'])

        # 렌더레이어를 사용하기로 되어있다면,
        # 서브미션을 각각 생성해서 던져주어야 한다.
        if self.render_layer_checkbox.isChecked():
            plugin.add('UsingRenderLayers', '1')
            plugin.add('UseLegacyRenderLayers', '1')
            for layer in pm.ls(type='renderLayer'):
                if 'defaultRenderLayer' in layer.name():
                    continue
                if layer.namespace() != '':
                    continue
                if not layer.renderable.get():
                    continue
                # 잡의 이름도 변경해준다.
                job.add('BatchName', self.job_name_field.text())
                job.add('Name', '{} - {}'.format(self.job_name_field.text(), layer))
                # 렌더레이어를 지정해준다.
                plugin.add('RenderLayer', layer)

                # Individual Render Layers 세팅을 확인한다.
                if layer.name() in individual_set:
                    data = individual_set[layer.name()]
                    job.add('Priority', data['priority'])
                    job.add('Pool', data['pool'])
                    job.add('SecondaryPool', data['sec_pool'])
                    job.add('Group', data['group'])
                    job.add('ConcurrentTasks', data['concurrent_task'])
                    job.add('ChunkSize', data['frame_per_task'])
                    plugin.add('GPUsPerTask', data['gpus_per_task'])
                else:
                    job.add('Priority', priority)
                    job.add('Pool', pool)
                    job.add('SecondaryPool', sec_pool)
                    job.add('Group', group)
                    job.add('ConcurrentTasks', concurrent_task)
                    job.add('ChunkSize', frame_per_task)
                    plugin.add('GPUsPerTask', gpus_per_task)

                # 데드라인에 던져준다.
                submission = moon.deadline.Submission(job, plugin, server_scene_file)
                submission.submit()
        else:
            submission = moon.deadline.Submission(job, plugin, server_scene_file)
            submission.submit()

        # 데드라인에 잡을 생성하여 전달하고 난 후 서브미터를 종료한다.
        self.accept()

    @staticmethod
    def get_deadline_command():
        path = os.environ['DEADLINE_PATH']
        if path:
            return pathjoin(path.replace(os.sep, '/'), 'deadlinecommand.exe')

    def get_deadline_pools(self):
        """데드라인에 설정된 그룹 리스트를 질의하여 반환한다."""
        deadline_command = self.get_deadline_command()
        command = [
            deadline_command,
            '-pools',
        ]
        result = subprocess.check_output(command, shell=True)
        return [x for x in result.split('\r\n') if x != '']

    def get_deadline_groups(self):
        """데드라인에 설정된 그룹 리스트를 질의하여 반환한다."""
        deadline_command = self.get_deadline_command()
        command = [
            deadline_command,
            '-groups',
        ]
        result = subprocess.check_output(command, shell=True)
        return [x for x in result.split('\r\n') if x != '']


class IndividualRenderLayerTable(QTableWidget):

    HEADER_LABELS = [
        'Render Layer',
        'Priority',
        'Pool',
        'Secodary\nPool',
        'Group',
        'Concurrent\nTask',
        'Frame\nPer Task',
        'GPUs\nPer Task',
    ]
    COLUMN_WIDTHS = [150, 50, 80, 80, 80, 100, 80, 80]
    OV_PREFIX = 'sm_deadline_submitter_individual_render_layer_table_header'

    def __init__(self, parent=None):
        super(IndividualRenderLayerTable, self).__init__(parent)
        self.parent = parent

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setCornerButtonEnabled(False)
        self.setWordWrap(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.header = self.horizontalHeader()
        self.header.sectionResized.connect(self.on_header_resized)

        self.clear()

    def init_cell_widths(self):
        for i, width in enumerate(self.COLUMN_WIDTHS):
            self.setColumnWidth(i, width)

    def _ov(self, index):
        return '{}{}'.format(self.OV_PREFIX, index)

    def on_header_resized(self, *args):
        index, old, value = args
        pm.optionVar(intValue=(self._ov(index), value))

    def clear(self, *args, **kwargs):
        super(IndividualRenderLayerTable, self).clear(*args, **kwargs)
        self.setColumnCount(len(self.HEADER_LABELS))
        self.setHorizontalHeaderLabels(self.HEADER_LABELS)
        self.setRowCount(0)
        for i, title in enumerate(self.HEADER_LABELS):
            ov = self._ov(i)
            if pm.optionVar(exists=ov):
                width = pm.optionVar(query=ov)
            else:
                width = self.COLUMN_WIDTHS[i]
            self.setColumnWidth(i, width)

    def add(self, data):
        row = self.rowCount()
        self.setRowCount(row + 1)

        item1 = QTableWidgetItem(data['render_layer'])
        item2 = QTableWidgetItem(data['priority'])
        item3 = QTableWidgetItem(data['pool'])
        item4 = QTableWidgetItem(data['sec_pool'])
        item5 = QTableWidgetItem(data['group'])
        item6 = QTableWidgetItem(data['concurrent_task'])
        item7 = QTableWidgetItem(data['frame_per_task'])
        item8 = QTableWidgetItem(data['gpus_per_task'])

        self.setItem(row, 0, item1)
        self.setItem(row, 1, item2)
        self.setItem(row, 2, item3)
        self.setItem(row, 3, item4)
        self.setItem(row, 4, item5)
        self.setItem(row, 5, item6)
        self.setItem(row, 6, item7)
        self.setItem(row, 7, item8)

        layer = pm.PyNode(data['render_layer'])
        for name in ['priority', 'pool', 'secondaryPool', 'group', 'concurrentTask', 'framePerTask', 'gpusPerTask']:
            deadline_attr_name = 'deadline' + name.title()
            if not layer.hasAttr(deadline_attr_name):
                pm.addAttr(layer, longName=deadline_attr_name, dataType='string')
        layer.deadlinePriority.set(data['priority'])
        layer.deadlinePool.set(data['pool'])
        layer.deadlineSecondaryPool.set(data['sec_pool'])
        layer.deadlineGroup.set(data['group'])
        layer.deadlineConcurrentTask.set(data['concurrent_task'])
        layer.deadlineFramePerTask.set(data['frame_per_task'])
        layer.deadlineGpusPerTask.set(data['gpus_per_task'])

    def get_data(self, row=None):
        data = {}

        if row is None:
            rows = range(self.rowCount())
        else:
            rows = [row]

        for r in rows:
            render_layer = self.item(r, 0).text()
            data[render_layer] = {
                'priority': self.item(r, 1).text(),
                'pool': self.item(r, 2).text(),
                'sec_pool': self.item(r, 3).text(),
                'group': self.item(r, 4).text(),
                'concurrent_task': self.item(r, 5).text(),
                'frame_per_task': self.item(r, 6).text(),
                'gpus_per_task': self.item(r, 7).text(),
            }

        return data

    def get_selected_row(self):
        ranges = self.selectedRanges()
        return ranges[0].topRow()

    def contextMenuEvent(self, e, *args, **kwargs):
        super(IndividualRenderLayerTable, self).contextMenuEvent(e, *args, **kwargs)

        # 아무런 아이템도 선택되지 않으면 컨텍스트 메뉴가 보이지 않는다.
        if not self.selectedIndexes():
            return

        # 컨텍스트 메뉴 생성
        menu = QMenu(self)

        edit = menu.addAction('Edit')
        remove = menu.addAction('Remove')

        # 사용자의 입력을 받아 원하는 기능을 수행하고 콜백을 보내준다.
        action = menu.exec_(self.mapToGlobal(e.pos()))

        row = self.get_selected_row()

        if action == edit:
            win = IndividualRenderLayerSettingCreateWindow(self.get_data(row), parent=self.parent)
            result = win.exec_()
            if result:
                data = win.get_data()
                self.item(row, 0).setText(data['render_layer'])
                self.item(row, 1).setText(data['priority'])
                self.item(row, 2).setText(data['pool'])
                self.item(row, 3).setText(data['sec_pool'])
                self.item(row, 4).setText(data['group'])
                self.item(row, 5).setText(data['concurrent_task'])
                self.item(row, 6).setText(data['frame_per_task'])
                self.item(row, 7).setText(data['gpus_per_task'])
        elif action == remove:
            self.removeRow(row)


class IndividualRenderLayerSettingCreateWindow(QDialog):

    def __init__(self, data=None, parent=None):
        super(IndividualRenderLayerSettingCreateWindow, self).__init__(parent)
        self.data = data
        self.parent = parent

        self.setWindowTitle('Individual Render Layer Creation')
        self.main_layout = QFormLayout(self)

        self.render_layer_combo = Combobox(korean=False)
        self.render_layer_combo.setMinimumSize(200, 22)

        self.pool_combo = Combobox(korean=False)
        self.pool_combo.setMinimumSize(100, 22)

        self.sec_pool_combo = Combobox(korean=False)
        self.sec_pool_combo.setMinimumSize(100, 22)

        self.group_combo = Combobox(korean=False)
        self.group_combo.setMinimumSize(100, 22)

        self.priority_field = QLineEdit()
        self.priority_field.setText(self.parent.PRIORITY)
        self.priority_field.setFixedWidth(50)

        self.chunk_size_field = QLineEdit()
        self.chunk_size_field.setFixedWidth(50)
        self.chunk_size_field.setText(self.parent.CHUNK_SIZE)

        self.concurrent_task_field = QLineEdit()
        self.concurrent_task_field.setFixedWidth(50)
        self.concurrent_task_field.setText(self.parent.CONCURRENT_TASK)

        self.gpu_per_task_field = QLineEdit()
        self.gpu_per_task_field.setFixedWidth(50)
        self.gpu_per_task_field.setText(self.parent.GPU_PER_TASK)

        ####################################################################################################
        # 버튼 레이아웃
        ####################################################################################################
        btn_layout = QHBoxLayout()

        ok_btn = Button('OK', korean=False)
        ok_btn.clicked.connect(self.check_accept)

        cancel_btn = Button('Cancel', korean=False)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        ####################################################################################################
        # 윈도우 레이아웃
        ####################################################################################################
        self.main_layout.addRow(QLabel('Render Layer'), self.render_layer_combo)
        self.main_layout.addRow(hline())
        self.main_layout.addRow(QLabel('Pool'), self.pool_combo)
        self.main_layout.addRow(QLabel('Secodary Pool'), self.sec_pool_combo)
        self.main_layout.addRow(QLabel('Group'), self.group_combo)
        self.main_layout.addRow(hline())
        self.main_layout.addRow(QLabel('Priority'), self.priority_field)
        self.main_layout.addRow(hline())
        self.main_layout.addRow(QLabel('Concurrent Task'), self.concurrent_task_field)
        self.main_layout.addRow(QLabel('Frame Per Task'), self.chunk_size_field)
        self.main_layout.addRow(QLabel('GPUs Per Task'), self.gpu_per_task_field)
        self.main_layout.addRow(hline())
        self.main_layout.addRow(btn_layout)

        self.init_values()

    def check_accept(self):
        if self.render_layer_combo.currentIndex() != 0:
            self.accept()

    def init_values(self):
        self.render_layer_combo.addItem('-- Render Layer --')
        for layer in reversed(pm.ls(type='renderLayer')):
            if 'defaultRenderLayer' in layer.name():
                continue
            if not layer.renderable.get():
                continue
            self.render_layer_combo.addItem(layer.name())

        for pool in self.parent.pools:
            self.pool_combo.addItem(pool)
            self.sec_pool_combo.addItem(pool)

        for grp in self.parent.groups:
            self.group_combo.addItem(grp)

        if self.data:
            render_layer = self.data.keys()[0]
            data = self.data[render_layer]
            self.render_layer_combo.setCurrentText(render_layer)
            self.priority_field.setText(data['priority'])
            self.pool_combo.setCurrentText(data['pool'])
            self.sec_pool_combo.setCurrentText(data['sec_pool'])
            self.group_combo.setCurrentText(data['group'])
            self.concurrent_task_field.setText(data['concurrent_task'])
            self.chunk_size_field.setText(data['frame_per_task'])
            self.gpu_per_task_field.setText(data['gpus_per_task'])

    def get_data(self):
        return {
            'render_layer': self.render_layer_combo.currentText(),
            'pool': self.pool_combo.currentText(),
            'sec_pool': self.sec_pool_combo.currentText(),
            'group': self.group_combo.currentText(),
            'priority': self.priority_field.text(),
            'concurrent_task': self.concurrent_task_field.text(),
            'frame_per_task': self.chunk_size_field.text(),
            'gpus_per_task': self.gpu_per_task_field.text(),
        }


@authorized
def main(parent=maya_widget()):
    global submitterwin

    try:
        submitterwin.close()
        submitterwin.deleteLater()
    except:
        pass

    submitterwin = DeadlineSubmitterWindow(parent=parent)
    submitterwin.show()
