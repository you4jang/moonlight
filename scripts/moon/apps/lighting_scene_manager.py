# -*- coding: utf-8 -*-
from moon.authentication import *
from moon.join import *
from moon.path import *
from moon.qt import *
from functools import partial

import re
import time
import shutil

import moon.clean
import moon.context
import moon.modelpanel
import moon.scriptjob
import moon.timeline
import moon.log
import moon.shotgun
import moon.apps.config as config

import maya.cmds as cmds
import pymel.core as pm

reload(moon.clean)
reload(moon.context)
reload(moon.modelpanel)
reload(moon.scriptjob)
reload(moon.timeline)
reload(moon.log)
reload(moon.shotgun)
reload(config)


log = moon.log.get_logger('lighting_scene_manager')


####################################################################################################
# 상수
####################################################################################################
SHOT_NAME_PATTERN = r'(?P<shot_name>(?P<ep>EP\d\d)_(?P<cut>C\d\d\d[A-Z]?))_Lgt$'


####################################################################################################
# 필터 전용 콤보박스 (우클릭 필터 삭제 기능 포함)
####################################################################################################
class FilterCombobox(Combobox):

    def __init__(self, init_script, *args, **kwargs):
        super(FilterCombobox, self).__init__(korean=False, *args, **kwargs)
        self.init_script = init_script

    def mouseReleaseEvent(self, e):
        reset = False
        if type(e) == QMouseEvent:
            if e.button() == Qt.MouseButton.RightButton:
                reset = True
        elif type(e) == QContextMenuEvent:
            reset = True
        if reset:
            if self.count() <= 1:
                return
            if self.currentIndex() < 1:
                return
            self.init_script()


class TitleLabel(Label):

    def __init__(self, txt, parent=None):
        super(TitleLabel, self).__init__(parent)
        self.setText(txt)
        self.setFixedHeight(20)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('color:#eee;background-color:#333')


class FunctionButton(Button):

    def __init__(self, *args, **kwargs):
        super(FunctionButton, self).__init__(*args, **kwargs)
        self.setEnabled(False)

    def enable(self):
        self.setEnabled(True)

    def disable(self):
        self.setEnabled(False)


####################################################################################################
# 스테이터스 클래스
####################################################################################################
class Status(object):

    STATUS_DATA = {
        'wtg': {
            'name': 'Waiting to Start',
            'color': ((255, 255, 255), (128, 128, 128)),
            'sort_order': 0,
        },
        'ip': {
            'name': 'In Progress',
            'color': ((30, 30, 30), (202, 225, 202)),
            'sort_order': 1,
        },
        'fin': {
            'name': 'Final',
            'color': ((255, 255, 255), (40, 160, 60)),
            'sort_order': 2,
        },
        'hld': {
            'name': 'On Hold',
            'color': ((0, 0, 0), (255, 255, 0)),
            'sort_order': 3,
        },
        'rrq': {
            'name': 'Revision Requested',
            'color': ((255, 255, 255), (230, 30, 40)),
            'sort_order': 4,
        },
    }

    @classmethod
    def get_list(cls):
        status_list = [None for x in range(len(cls.STATUS_DATA.values()))]
        for data in cls.STATUS_DATA.values():
            idx = data['sort_order']
            status_list[idx] = data['name']
        return status_list

    @classmethod
    def get_code(cls, name):
        for code, data in cls.STATUS_DATA.items():
            if data['name'] == name:
                return code

    @classmethod
    def get_name(cls, code):
        if code in cls.STATUS_DATA:
            return cls.STATUS_DATA[code]['name']
        else:
            return code

    @classmethod
    def get_color(cls, code):
        if code in cls.STATUS_DATA:
            return cls.STATUS_DATA[code]['color']
        else:
            return (255, 255, 255), (128, 128, 128)


####################################################################################################
# 작업리스트 클래스
####################################################################################################
class WorkList(QTableWidget):

    def __init__(self, parent=None):
        super(WorkList, self).__init__(parent)
        self.parent = parent
        self.ui()

    def ui(self):
        self.header_labels = ['Shot', 'Start', 'End', 'Ani\nFile', 'Ani\nStatus', 'Lighting\nStatus', 'Updated At']
        self.column_widths = [100, 60, 60, 60, 100, 120, 150]

        self.field_width_data_optionvar = self.parent.objectName() + '_header_width_optionvar'

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        self.setCornerButtonEnabled(False)
        self.setWordWrap(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.doubleClicked.connect(self.open_work_with_dialog)

        self.header = self.horizontalHeader()
        # self.header.setStretchLastSection(True)
        self.header.sectionResized.connect(self.on_header_resized)

        self.init_header()

    def _ov(self, index):
        return '{}{}'.format(self.field_width_data_optionvar, index)

    def init(self):
        self.init_header()
        self.setRowCount(0)
        self.setSortingEnabled(True)

    def init_cell_widths(self):
        for i, width in enumerate(self.column_widths):
            self.setColumnWidth(i, width)

    def init_header(self):
        # 헤더에 개수를 파악하고, 비어있는 열을 만든다.
        # 헤더에 이름을 지정한다.
        self.setColumnCount(len(self.header_labels))
        self.setHorizontalHeaderLabels(self.header_labels)
        for i, title in enumerate(self.header_labels):
            ov = self._ov(i)
            if cmds.optionVar(exists=ov):
                width = cmds.optionVar(query=ov)
            else:
                width = self.column_widths[i]
            self.setColumnWidth(i, width)

    def on_header_resized(self, *args):
        index, old, value = args
        cmds.optionVar(intValue=(self._ov(index), value))
        self.setWordWrap(True)

    def open_work_with_dialog(self):
        # 아무런 아이템도 선택되지 않으면 컨텍스트 메뉴가 보이지 않는다.
        if not self.selectedIndexes():
            return
        if self.is_multi_selected():
            return
        # 사용자의 입력을 받아 원하는 기능을 수행하고 콜백을 보내준다.
        self._execute(self._execute_single_job_as_func, partial(self.parent.open_work))

    def is_single_selected(self):
        return len(self.get_selected_indexes()) == 1

    def is_multi_selected(self):
        return len(self.get_selected_indexes()) > 1

    def get_selected_single_sg_task(self):
        ranges = self.selectedRanges()
        row = ranges[0].topRow()
        return self.item(row, 0).work

    def get_selected_multi_sg_task(self):
        works = []
        for row in self.get_selected_indexes():
            works.append(self.item(row, 0).work)
        return works

    def get_selected_indexes(self):
        ranges = self.selectedRanges()
        selected = []
        for rgn in ranges:
            top_row = rgn.topRow()
            for i in range(rgn.rowCount()):
                row = top_row + i
                selected.append(row)
        return sorted(selected)

    def get_selected_work_names(self):
        selected = []
        for i in self.get_selected_indexes():
            work = self.item(i, 0).work
            selected.append(self.item(i, 0).work['entity']['name'])
        to_string = ', '.join(selected)
        if len(to_string) > 25:
            to_string = to_string[:25] + '...'
        return to_string

    @staticmethod
    def _execute(executer, callback):
        args = None
        kwargs = None

        if isinstance(callback, partial):
            func = callback.func
            args = callback.args
            kwargs = callback.keywords
        else:
            func = callback

        executer(func, *args or (), **kwargs or {})

    def _execute_single_job_as_func(self, callback, *args, **kwargs):
        callback(self.get_selected_single_sg_task(), *args, **kwargs)

    def _execute_multi_job_as_func(self, callback, *args, **kwargs):
        callback(self.get_selected_multi_sg_task(), *args, **kwargs)


class LightingSceneManagerWindow(MainWindow):

    STORED_PROJECT_INDEX_OPTIONVAR = 'lighting_scene_manager_stored_project_index_optionvar'
    FILTER_NAME_EPISODE = '- Episode -'
    FILTER_NAME_STATUS = '- Status -'

    def __init__(self, parent=maya_widget()):
        super(LightingSceneManagerWindow, self).__init__(parent)
        self.task_names = ['Lighting']

        # 마지막으로 검색한 방식이 무엇인지 저장할 변수
        # 검색 방식에는
        #   1. 필터링 조건을 이용한 검색 (filter)
        #   2. 현재 씬 파일 파악 검색 (current)
        # 등 2가지가 있다.
        self.last_searching_mode = None

        # 기능 버튼 모음 리스트
        self.function_button_list = []

        self.ui()
        self.init_filters()
        self.init_current_scene()
        self.count_work_list_items()

    def ui(self):
        self.setWindowTitle('ksd6 - Lighting Scene Manager')
        self.setObjectName('hb_lighting_scene_manager_window')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.window_layout = QVBoxLayout(self.central_widget)
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(0)
        self.window_layout.setAlignment(Qt.AlignTop)

        self.center_layout = QHBoxLayout()
        self.center_layout.setContentsMargins(9, 9, 9, 9)
        self.center_layout.setSpacing(6)

        ####################################################################################################
        # 좌측 레이아웃
        ####################################################################################################
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignTop)
        self.left_layout.setSpacing(1)

        self.sg_open_btn = FunctionButton('샷건 페이지')
        self.sg_open_btn.setIcon(QIcon(img_path('sg_logo.png')))
        self.sg_open_btn.clicked.connect(self.open_sg_shot_page)
        self.function_button_list.append(self.sg_open_btn)

        folder_label = TitleLabel('폴더')
        self.an_folder_btn = FunctionButton('애니 폴더')
        self.an_folder_btn.setIcon(QIcon(img_path('open.png')))
        self.an_folder_btn.clicked.connect(self.open_an_folder)
        self.function_button_list.append(self.an_folder_btn)

        self.lt_folder_btn = FunctionButton('라이팅 폴더')
        self.lt_folder_btn.setIcon(QIcon(img_path('open.png')))
        self.lt_folder_btn.clicked.connect(self.open_lt_folder)
        self.function_button_list.append(self.lt_folder_btn)

        open_label = TitleLabel('씬 파일')
        self.an_open_btn = FunctionButton('애니 열기')
        self.an_open_btn.clicked.connect(self.open_an_file)
        self.function_button_list.append(self.an_open_btn)
        self.lt_create_btn = FunctionButton('라이팅 생성')
        self.lt_create_btn.clicked.connect(self.create_lt_file)
        self.function_button_list.append(self.lt_create_btn)
        self.lt_open_btn1 = FunctionButton('라이팅 열기')
        self.lt_open_btn1.clicked.connect(self.open_lt_file)
        self.function_button_list.append(self.lt_open_btn1)

        status_label = TitleLabel('상태변경')
        self.status_wtg_btn = FunctionButton('Waiting to Start', korean=False)
        self.status_wtg_btn.clicked.connect(partial(self.set_status, 'wtg'))
        self.function_button_list.append(self.status_wtg_btn)
        self.status_ip_btn = FunctionButton('In Progress', korean=False)
        self.status_ip_btn.clicked.connect(partial(self.set_status, 'ip'))
        self.function_button_list.append(self.status_ip_btn)
        self.status_fin_btn = FunctionButton('Final', korean=False)
        self.status_fin_btn.clicked.connect(partial(self.set_status, 'fin'))
        self.function_button_list.append(self.status_fin_btn)
        self.status_rrq_btn = FunctionButton('Revision Requested', korean=False)
        self.status_rrq_btn.clicked.connect(partial(self.set_status, 'rrq'))
        self.function_button_list.append(self.status_rrq_btn)

        self.left_layout.addItem(QSpacerItem(0, 33))
        self.left_layout.addWidget(self.sg_open_btn)
        self.left_layout.addItem(QSpacerItem(0, 15))
        self.left_layout.addWidget(folder_label)
        self.left_layout.addWidget(self.an_folder_btn)
        self.left_layout.addWidget(self.lt_folder_btn)
        self.left_layout.addItem(QSpacerItem(0, 15))
        self.left_layout.addWidget(open_label)
        self.left_layout.addWidget(self.an_open_btn)
        self.left_layout.addWidget(self.lt_create_btn)
        self.left_layout.addWidget(self.lt_open_btn1)
        self.left_layout.addItem(QSpacerItem(0, 15))
        self.left_layout.addWidget(status_label)
        self.left_layout.addWidget(self.status_wtg_btn)
        self.left_layout.addWidget(self.status_ip_btn)
        self.left_layout.addWidget(self.status_fin_btn)
        self.left_layout.addWidget(self.status_rrq_btn)

        ####################################################################################################
        # 메인 레이아웃
        ####################################################################################################
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(Qt.AlignTop)

        # 줄 간격 초기화 버튼
        self.clear_width_btn = IconButton('width.png', 25, 17)
        self.clear_width_btn.setToolTip('Reset width on headers.')
        self.clear_width_btn.clicked.connect(self.init_work_list_header_widths)

        self.filter_grp = Groupbox()
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_layout.setSpacing(6)

        self.project_filter_combo = Combobox(korean=False)
        self.project_filter_combo.setView(QListView())
        self.project_filter_combo.setFixedSize(130, 25)

        self.episode_filter_combo = FilterCombobox(self.init_episode_filter)
        self.episode_filter_combo.setView(QListView())
        self.episode_filter_combo.setFixedSize(100, 25)
        self.episode_filter_combo.currentIndexChanged.connect(partial(Combobox.toggle_highlight, self.episode_filter_combo))

        self.status_filter_combo = FilterCombobox(self.init_status_filter)
        self.status_filter_combo.setView(QListView())
        self.status_filter_combo.setFixedSize(130, 25)
        self.status_filter_combo.currentIndexChanged.connect(partial(Combobox.toggle_highlight, self.status_filter_combo))

        # 검색버튼
        self.search_btn = Button('검색')
        self.search_btn.setIcon(QIcon(img_path('magnifying-glass.png')))
        self.search_btn.setIconSize(QSize(12, 12))
        self.search_btn.setFixedWidth(120)
        self.search_btn.setFixedHeight(25)
        self.search_btn.setStyleSheet(stylesheet({
            'QPushButton': [
                'border-radius: 3px',
                'border: 1px solid #333333',
                'background-color: #008800',
            ],
            'QPushButton:enabled::hover': [
                'background-color: #00aa00',
            ],
        }))
        self.search_btn.clicked.connect(self.search_tasks)

        # 키워드 검색
        self.keyworkd_field = LineEdit()
        self.keyworkd_field.setFixedWidth(100)
        self.keyworkd_field.setFixedHeight(25)
        self.keyworkd_field.returnPressed.connect(self.search_from_keyword)

        # 현재 열려있는 작업 검색 버튼
        open_work_btn = IconButton('target.png', 25, 13)
        open_work_btn.setToolTip('현재 열려있는 씬 파일을 찾아줍니다.')
        open_work_btn.clicked.connect(self.init_current_scene)

        self.filter_layout.addWidget(self.clear_width_btn)
        self.filter_layout.addItem(QSpacerItem(5, 0))
        self.filter_layout.addWidget(self.project_filter_combo)
        self.filter_layout.addWidget(self.episode_filter_combo)
        self.filter_layout.addWidget(self.status_filter_combo)
        self.filter_layout.addItem(QSpacerItem(5, 0))
        self.filter_layout.addWidget(self.search_btn)
        self.filter_layout.addWidget(open_work_btn)
        self.filter_layout.addWidget(self.keyworkd_field)
        self.filter_layout.addItem(QSpacerItem(5, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        # 작업리스트
        self.work_list_grp = QWidget()
        self.work_list_layout = QVBoxLayout(self.work_list_grp)
        self.work_list_layout.setContentsMargins(0, 0, 0, 0)
        self.work_list_layout.setAlignment(Qt.AlignTop)
        self.work_list_layout.setSpacing(6)

        # 메인 위젯
        self.work_list = WorkList(parent=self)
        self.work_list.itemSelectionChanged.connect(self.on_item_selection_changed)

        # 총 작업 개수 및 선택 개수
        self.count_layout = QHBoxLayout()

        self.work_count = Label()
        self.latest_search_time = Label()

        self.count_layout.addWidget(self.work_count)
        self.count_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.count_layout.addWidget(self.latest_search_time)

        # 작업목록 배치
        self.work_list_layout.addWidget(self.work_list)
        self.work_list_layout.addLayout(self.count_layout)

        ####################################################################################################
        # 오른쪽 레이아웃
        ####################################################################################################
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignTop)
        self.right_layout.setSpacing(1)

        render_set_btn = Button('렌더 글로벌 셋')
        render_set_btn.clicked.connect(self.set_render_global_set)

        deadline_submitter_btn = Button('데드라인 서브미터')
        deadline_submitter_btn.clicked.connect(self.open_deadline_submitter)

        copy_btn = Button('씬 복사')
        copy_btn.clicked.connect(self.copy_scene_to)

        self.right_layout.addItem(QSpacerItem(0, 33))
        self.right_layout.addWidget(render_set_btn)
        self.right_layout.addWidget(deadline_submitter_btn)
        self.right_layout.addItem(QSpacerItem(0, 10))
        self.right_layout.addWidget(copy_btn)

        ####################################################################################################
        # 레이아웃 배치
        ####################################################################################################
        self.main_layout.addLayout(self.filter_layout)
        self.main_layout.addWidget(self.work_list_grp)

        self.center_layout.addLayout(self.left_layout)
        self.center_layout.addLayout(self.main_layout)
        self.center_layout.addLayout(self.right_layout)

        self.window_layout.addLayout(self.center_layout)

        restore_window(self)

        self.setMinimumSize(800, 700)

    def open_sg_shot_page(self):
        sg_task = self.work_list.get_selected_single_sg_task()
        sg = self.get_sg_connection('admin_api')
        url = '{}/detail/Shot/{}'.format(sg.SHOTGUN_URL, sg_task['entity']['id'])
        os.startfile(url)

    def open_an_folder(self):
        sg_task = self.work_list.get_selected_single_sg_task()
        path = dirs(self.get_server_ani_path(sg_task['entity']['name']))
        log.debug('ani path : {}'.format(path))
        if os.path.isdir(path):
            open_folder(path)

    def open_lt_folder(self):
        sg_task = self.work_list.get_selected_single_sg_task()
        path = dirs(self.get_server_path(sg_task['entity']['name']))
        open_folder(path)

    def open_an_file(self):
        sg_task = self.work_list.get_selected_single_sg_task()
        an_file = self.get_server_ani_file(sg_task['entity']['name'])
        log.debug('an_file : {}'.format(an_file))
        if not os.path.isfile(an_file):
            errorbox('애니 씬 파일이 존재하지 않습니다.', parent=self)
            return
        if save_changes(parent=self):
            cmds.file(an_file, force=True, open=True, ignoreVersion=True, prompt=False, options='v=0')

    def open_deadline_submitter(self):
        import moon.apps.deadline_submitter
        reload(moon.apps.deadline_submitter)
        moon.apps.deadline_submitter.main(self)

    def open_lt_file(self, in_progress=False):
        sg_task = self.work_list.get_selected_single_sg_task()
        if in_progress:
            self.open_work(sg_task, status='ip')
        else:
            self.open_work(sg_task)

    def create_lt_file(self):
        sg_task = self.work_list.get_selected_single_sg_task()
        self.open_work(sg_task, status='ip', create=True)

    def init_work_list_header_widths(self):
        self.work_list.init_cell_widths()

    def init_project_filter(self):
        log.debug('init_project_filter()')
        project_list = [
            {
                'type': 'Project',
                'id': 122,
                'name': 'Dance6 Project',
            },
            {
                'type': 'Project',
                'id': 155,
                'name': 'Kongsuni7_Project',
            },
        ]
        disconnect(self.project_filter_combo.currentIndexChanged)
        self.project_filter_combo.clear()
        for i, sg_prj in enumerate(project_list):
            self.project_filter_combo.addItem(sg_prj['name'])
            self.project_filter_combo.setItemData(i, sg_prj)
        if pm.optionVar(exists=self.STORED_PROJECT_INDEX_OPTIONVAR):
            idx = pm.optionVar(query=self.STORED_PROJECT_INDEX_OPTIONVAR)
            self.project_filter_combo.setCurrentIndex(idx)
        self.project_filter_combo.currentIndexChanged.connect(self.on_project_changed)
        self.init_episode_filter()

    def init_episode_filter(self):
        log.debug('init_episode_filter()')

        self.episode_filter_combo.clear()
        self.episode_filter_combo.addItem(self.FILTER_NAME_EPISODE)

        sg = self.get_sg_connection('admin_api')
        filters = [
            ['project', 'is', self.get_selected_sg_project()],
        ]
        order = [
            {'field_name': 'code', 'direction': 'asc'},
        ]

        for sg_episode in sg.find(str('Episode'), filters, ['code'], order):
            self.episode_filter_combo.addItem(sg_episode['code'].split('_')[-1])

    def init_status_filter(self):
        log.debug('init_status_filter()')
        self.status_filter_combo.clear()
        self.status_filter_combo.addItem(self.FILTER_NAME_STATUS)
        for status in Status.get_list():
            self.status_filter_combo.addItem(status)

    def search_from_keyword(self):
        k = self.keyworkd_field.text()
        self.keyworkd_field.clear()
        if len(k) < 5 or len(k) > 6:
            return
        ep = k[:2]
        cut = k[2:]
        shot_name = 'EP{}_C{}'.format(ep, cut)
        self.search_tasks(shot=shot_name)

    def search_tasks(self, shot=None, filtered_task_list=None, clear=False):
        log.debug('search_tasks(shot={}, filtered_task_list={}, clear={})'.format(shot, filtered_task_list, clear))

        # 작업 목록을 모두 지우고 카운트를 초기화한다.
        self.work_list.init()
        self.count_work_list_items()

        # 단순히 리스트만 초기화하고 싶을 때는 실행을 종료한다.
        if clear:
            return

        # 검색에 소요된 시간을 알아보기 위해 시작시간을 설정한다.
        start_time = time.time()

        # 마지막으로 검색한 모드가 필터를 이용한 검색인지 현재 파일이름을 근거로 샷 이름을 추적한 검색인지 파악해놓는다.
        self.last_searching_mode = 'current' if shot else 'filter'

        status = self.get_selected_status()

        sg = self.get_sg_connection('admin_api')
        sg_project = self.get_selected_sg_project()
        lgt_filters = [
            ['project', 'is', sg_project],
            ['step', 'is', config.SG_STEP_LIGHTING],
            ['content', 'is', 'Lighting'],
        ]

        anfx_filters = [
            ['project', 'is', sg_project],
            {
                'filter_operator': 'any',
                'filters': [
                    ['step', 'is', config.SG_STEP_ANIMATION],
                    ['step', 'is', config.SG_STEP_FX],
                ]
            }
        ]

        if shot:
            lgt_filters.append(['entity.Shot.code', 'is', shot])
            anfx_filters.append(['entity.Shot.code', 'is', shot])
        else:
            ep = self.get_selected_episode()
            if ep:
                lgt_filters.append(['entity.Shot.sg_episode.Episode.code', 'is', ep])
                anfx_filters.append(['entity.Shot.sg_episode.Episode.code', 'is', ep])

        if status:
            sg_status_code = Status.get_code(status)
            lgt_filters.append(['sg_status_list', 'is', sg_status_code])

        lgt_fields = [
            'content',
            'entity',
            'entity.Shot.sg_cut_in',
            'entity.Shot.sg_cut_out',
            'task_assignees',
            'sg_status_list',
            'updated_at',
            'sg_description',
            'step',
        ]

        anfx_fields = [
            'content',
            'entity',
            'step',
            'sg_status_list',
        ]

        order = [
            {'field_name': 'entity.Shot.code', 'direction': 'asc'},
            {'field_name': 'sg_sort_order', 'direction': 'asc'},
        ]

        lgt_sg_tasks = sg.find('Task', lgt_filters, lgt_fields, order)
        anfx_sg_tasks = sg.find('Task', anfx_filters, anfx_fields, order)

        # 가져온 태스크 리스트에서 Animation, FX 태스크를 정리한다.
        an_sg_task_list = {}
        for sg_task in anfx_sg_tasks:
            step_name = sg_task['step']['name']
            shot_name = sg_task['entity']['name']
            if step_name == 'Animation':
                an_sg_task_list[shot_name] = sg_task['sg_status_list']
                continue

        # 작업을 리스트에 넣기 전에 정렬 기능을 반드시 꺼야한다.
        self.work_list.setSortingEnabled(False)
        # 작업의 개수를 파악하여 row를 생성한다.
        self.work_list.setRowCount(len(lgt_sg_tasks))

        for row, sg_task in enumerate(lgt_sg_tasks):
            shot_name = sg_task['entity']['name']
            task_name = sg_task['content']

            shot_name_item = QTableWidgetItem(shot_name)
            shot_name_item.work = sg_task

            # 태스크 이름
            task_name_item = QTableWidgetItem(task_name)
            task_name_item.setTextAlignment(Qt.AlignCenter)

            # 진행상태
            status = sg_task['sg_status_list']
            lt_status_item = QTableWidgetItem(Status.get_name(status))
            lt_status_item.setTextAlignment(Qt.AlignCenter)
            fore_color, back_color = Status.get_color(status)
            if fore_color:
                lt_status_item.setForeground(QColor(*fore_color))
            if back_color:
                lt_status_item.setBackground(QColor(*back_color))

            # 애니 파일 유무
            an_file_item = QTableWidgetItem()
            an_file_item.setTextAlignment(Qt.AlignCenter)
            an_file = self.get_server_ani_file(sg_task['entity']['name'])
            if os.path.isfile(an_file):
                an_file_item.setText('O')
                an_file_item.setForeground(QColor(Qt.green))
            else:
                an_file_item.setText('n/a')
                an_file_item.setForeground(QColor(Qt.red))

            # AN 스테이터스
            an_status = an_sg_task_list[shot_name]
            an_status_item = QTableWidgetItem(Status.get_name(an_status))
            an_status_item.setTextAlignment(Qt.AlignCenter)
            fore_color, back_color = Status.get_color(an_status)
            if fore_color:
                an_status_item.setForeground(QColor(*fore_color))
            if back_color:
                an_status_item.setBackground(QColor(*back_color))

            # 시작프레임
            st_frame = sg_task['entity.Shot.sg_cut_in']
            if st_frame:
                st_frame_item = QTableWidgetItem(str(st_frame))
            else:
                st_frame_item = QTableWidgetItem()
            st_frame_item.setTextAlignment(Qt.AlignCenter)

            # 끝프레임
            ed_frame = sg_task['entity.Shot.sg_cut_out']
            if ed_frame:
                ed_frame_item = QTableWidgetItem(str(ed_frame))
            else:
                ed_frame_item = QTableWidgetItem()
            ed_frame_item.setTextAlignment(Qt.AlignCenter)

            # 최근 수정 날짜
            updated_item = QTableWidgetItem(sg_task['updated_at'].strftime('%Y-%m-%d %H:%M:%S'))
            updated_item.setTextAlignment(Qt.AlignCenter)

            self.work_list.setItem(row, 0, shot_name_item)
            self.work_list.setItem(row, 1, st_frame_item)
            self.work_list.setItem(row, 2, ed_frame_item)
            self.work_list.setItem(row, 3, an_file_item)
            self.work_list.setItem(row, 4, an_status_item)
            self.work_list.setItem(row, 5, lt_status_item)
            self.work_list.setItem(row, 6, updated_item)

        # 작업을 리스트에 넣기 전에 정렬 기능을 반드시 꺼야한다.
        self.work_list.setSortingEnabled(True)

        self.count_work_list_items()
        self.show_latest_search_time(elapsed_time=time.time() - start_time)

        self.work_list.setEnabled(True)
        self.work_list.resizeRowsToContents()

    def init_filters(self):
        log.debug('init_filters()')
        self.init_project_filter()
        self.init_status_filter()

    def init_current_scene(self):
        log.debug('init_current_scene()')

        # 현재 씬 파일의 이름을 파악한다.
        current_file = cmds.file(query=True, sceneName=True)
        log.debug('current_file : {}'.format(current_file))
        if not current_file:
            self.search_tasks(clear=True)
            return

        path = os.path.dirname(current_file)
        filename = basenameex(current_file)

        regex = re.match(SHOT_NAME_PATTERN, filename)
        log.debug('filename : {}'.format(filename))
        log.debug('regex : {}'.format(regex))
        if not regex:
            self.search_tasks(clear=True)
            return

        shot = regex.group('shot_name')
        step = path.split('/')[-1]

        self.search_tasks(shot=shot, filtered_task_list=step)

    def get_selected_sg_project(self):
        idx = self.project_filter_combo.currentIndex()
        return self.project_filter_combo.itemData(idx)

    def get_sg_connection(self, name):
        if not hasattr(self, 'sg_connections'):
            self.sg_connections = {}
        if name not in self.sg_connections:
            sg = moon.shotgun.Shotgun(name)
            self.sg_connections[name] = sg
        return self.sg_connections[name]

    def get_selected_my_work(self):
        return self.my_work_checkbox.isChecked()

    def get_selected_episode(self):
        if self.episode_filter_combo.currentIndex() == 0:
            return
        return self.episode_filter_combo.currentText()

    def get_selected_status(self):
        if self.status_filter_combo.currentIndex() == 0:
            return
        return self.status_filter_combo.currentText()

    def get_server_root_path(self):
        idx = self.project_filter_combo.currentIndex()
        if idx == 0:
            path = pathjoin('K:', 'KongsuniDance6')
        else:
            path = pathjoin('K:', 'Kongsuni7')
        return path

    def get_server_path(self, shot_name):
        ep = shot_name.split('_')[0]
        return dirs(pathjoin(self.get_server_root_path(), '04_LRComp', '01_Lighting', ep))

    def get_server_ren_path(self):
        return dirs(pathjoin(self.get_server_root_path(), '04_LRComp', '04_Render'))

    @staticmethod
    def get_episode_from_shot(shot_name):
        buf = shot_name.split('_')
        return buf[0]

    @staticmethod
    def get_cut_from_shot(shot_name):
        buf = shot_name.split('_')
        return buf[1]

    def get_server_ani_path(self, shot_name):
        ep = self.get_episode_from_shot(shot_name)
        cut = self.get_cut_from_shot(shot_name)
        return pathjoin(self.get_server_root_path(), '03_Animation', '02_Scenes', ep, cut, 'fdb')

    def get_server_ani_file(self, shot_name):
        buf = shot_name.split('_')
        ep = buf[0]
        cut = buf[1]
        path = self.get_server_ani_path(shot_name)
        if not path:
            return

        return pathjoin(path, namejoin(ep, cut, 'fdb', 'v001.ma'))

    def get_server_file(self, name):
        path = dirs(self.get_server_path(name))
        return pathjoin(path, name + '_Lgt.ma')

    def copy_scene_to(self):
        cur = cmds.file(query=True, sceneName=True, shortName=True)
        if not cur:
            return
        buf = basenameex(cur).split('_')
        ep = buf[0]
        cut = buf[1]

        win = CopyToWindow(ep, cut, self.get_sg_connection('admin_api'), parent=self)
        result = win.exec_()
        if not result:
            return
        dst_ep, dst_cut = win.get_target_info()

        src_shot_name = namejoin(ep, cut)
        dst_shot_name = namejoin(dst_ep, dst_cut)
        log.debug('dst_shot_name: {}'.format(dst_shot_name))

        src_file = cmds.file(query=True, sceneName=True)

        dst_path = self.get_server_path(dst_shot_name)
        dst_file = self.get_server_file(dst_shot_name)

        # 이미 파일이 존재하고 있을 때는 어떻게 할 것인가?
        # 덮어쓰기 할 지 물어본다.
        buttons = overwrite, cancel = '덮어쓰기', '취소'
        if os.path.isfile(dst_file):
            result = questionbox(
                parent=self,
                title='대상 파일 있음!',
                message='복사하려는 파일이 이미 존재합니다.',
                icon='question',
                button=buttons,
                default=overwrite,
                cancel=cancel,
                dismiss=cancel,
            )
            if result == cancel:
                return

        dirs(dst_path)
        cmds.file(rename=dst_file)
        cmds.file(force=True, save=True)

        dst_an_file = self.get_server_ani_file(dst_shot_name)
        log.debug('dst_an_file : {}'.format(dst_an_file))

        for ref in pm.ls(type='reference'):
            if ref.name() != '{}_fdb_v001RN'.format(src_shot_name):
                continue
            pm.lockNode(ref, lock=False)
            ref.rename('{}_fdb_v001RN'.format(dst_shot_name))
            pm.lockNode(ref, lock=True)
            cmds.file(dst_an_file, loadReference=ref.name(), options='v=0', prompt=False, ignoreVersion=True)
            break

        sg = self.get_sg_connection('admin_api')
        filters = [
            ['project', 'is', self.get_selected_sg_project()],
            ['step', 'is', config.SG_STEP_LIGHTING],
            ['content', 'is', 'Lighting'],
            ['entity.Shot.code', 'is', dst_shot_name],
        ]
        fields = [
            'content',
            'entity',
            'entity.Shot.sg_cut_in',
            'entity.Shot.sg_cut_out',
            'task_assignees',
            'sg_status_list',
            'updated_at',
            'sg_description',
            'step',
        ]

        sg_task = sg.find_one('Task', filters, fields)

        self.init_scene_openning_set(sg_task, 'ip')

        msg = Message()
        msg.title('파일복사 완료')
        msg.add('선택한 파일의 복사가 완료되었습니다.')
        msg.br()
        msg.add('원본파일 : {}'.format(src_file))
        msg.add('대상파일 : {}'.format(dst_file))
        infobox(msg, self)

    def count_work_list_items(self):
        total_count = self.work_list.rowCount()
        self.work_count.setText('전체 <span style="color:lightgreen"><b>{}</b></span> 태스크'.format(total_count))

    def set_status(self, code):
        sg_tasks = self.work_list.get_selected_multi_sg_task()
        sg = self.get_sg_connection('admin_api')
        for sg_task in sg_tasks:
            data = {'sg_status_list': code}
            sg.update('Task', sg_task['id'], data)
        self.reload_ui()

    @staticmethod
    def set_render_global_set():
        pm.undoInfo(openChunk=True)

        # 카메라 Far Clip 설정
        for cam in [x for x in cmds.ls(type='camera')]:
            try:
                cmds.setAttr(cam + '.farClipPlane', 100000000)
            except:
                pass

        current_render_layer = pm.editRenderLayerGlobals(query=True, currentRenderLayer=True)

        pm.loadPlugin('vrayformaya', quiet=True)

        # 레드쉬프트 렌더러로 변경
        render_globals = pm.PyNode('defaultRenderGlobals')
        pm.mel.eval('unifiedRenderGlobalsWindow();')
        pm.mel.eval('fillSelectedTabForCurrentRenderer();')
        pm.mel.eval('updateCurrentRendererSel("unifiedRenderGlobalsRendererSelOptionMenu");')
        render_globals.currentRenderer.set(lock=False)
        render_globals.currentRenderer.set('vray')
        pm.mel.eval('rendererChanged')

        vray_settings = pm.PyNode('vraySettings')
        vray_settings.animType.set(True)
        vray_settings.animBatchOnly.set(True)
        render_globals.startFrame.set(pm.playbackOptions(query=True, minTime=True))
        render_globals.endFrame.set(pm.playbackOptions(query=True, maxTime=True))

        pm.editRenderLayerGlobals(currentRenderLayer=current_render_layer)
        pm.undoInfo(closeChunk=True)

    def show_latest_search_time(self, elapsed_time=None):
        message = '검색소요시간 <b>{:.02f}초</b>'.format(elapsed_time)
        self.latest_search_time.setText(message)

    @staticmethod
    def determine_work(sg_task):
        from pprint import pprint, pformat
        pprint(sg_task)

    @authorized
    def open_work(self, sg_task, status=None, complete_message=True, create=False, replace=None):
        shot_name = sg_task['entity']['name']

        sv_ani_file = self.get_server_ani_file(shot_name)
        log.debug('sv_ani_file : {}'.format(sv_ani_file))

        sv_scn_file = self.get_server_file(shot_name)
        log.debug('sv_scn_file : {}'.format(sv_scn_file))

        cur = cmds.file(query=True, sceneName=True)
        if cur.lower() == sv_scn_file.lower():
            return

        if cmds.file(query=True, modified=True):
            buttons = save, ignore, cancel = '저장', '저장하지 않음', '취소'
            msg = Message(korean=True)
            msg.add('현재 씬 파일이 변경되었습니다. 저장하고 진행할까요?')
            res = questionbox(
                parent=self,
                message=msg,
                icon='question',
                button=buttons,
                default=save,
                cancel=cancel,
                dismiss=cancel,
            )
            if res == cancel:
                return
            elif res == save:
                cmds.file(force=True, save=True)

        # Status를 변경해야하는지 여부
        if status is not None:
            if sg_task['sg_status_list'] not in ['wtg', 'rrq', 'hld']:
                status = None

        if create:
            if os.path.isfile(sv_ani_file):
                sg = self.get_sg_connection('admin_api')
                filters = [
                    ['id', 'is', sg_task['entity']['id']],
                ]
                fields = ['sg_bg', 'sg_light_set']
                sg_shot = sg.find_one('Shot', filters, fields)
                if not sg_shot:
                    errorbox('샷건에 Shot이 없습니다.', parent=self)
                    return
                bg_set = sg_shot['sg_bg'][0]['name']
                if not bg_set:
                    errorbox('샷건에서 BG 어셋이 지정되어있지 않습니다.', parent=self)
                    return
                lt_set = sg_shot['sg_light_set']
                if not lt_set:
                    errorbox('샷건에서 라이팅 셋이 지정되어있지 않습니다.', parent=self)
                    return
                lt_set_path = pathjoin(config.SV_LIGHT_SET_PATH, bg_set)
                lt_set_file = pathjoin(lt_set_path, namejoin(bg_set, lt_set) + '.ma')
                log.debug('lt_set_file : {}'.format(lt_set_file))
                cmds.file(lt_set_file, force=True, open=True, ignoreVersion=True, prompt=False)
                cmds.file(rename=sv_scn_file)
                cmds.file(
                    sv_ani_file,
                    reference=True,
                    namespace=':',
                    # prompt=False,
                    options='v=0',
                    ignoreVersion=True,
                )
                cmds.file(force=True, save=True)
            else:
                errorbox('라이팅 씬 파일을 최초로 생성하려 하는데, 애니 씬 파일이 없습니다.', parent=self)
                return
        else:
            if os.path.isfile(sv_scn_file):
                cmds.file(
                    sv_scn_file,
                    force=True,
                    open=True,
                    # prompt=False,
                    ignoreVersion=True,
                    preserveReferences=True,
                )
            else:
                errorbox('라이팅 씬 파일이 없습니다.', parent=self)

        self.init_scene_openning_set(sg_task, status)

        if complete_message:
            msg = Message()
            msg.title('파일 열기 완료')
            msg.add('씬 파일이 열렸습니다.')
            msg.br()
            msg.add('파일이름 :')
            msg.add_filename(sv_scn_file)
            msg.br()
            msg.add('진행상태(Status) 변경 :')
            if status is not None:
                msg.add_filename(Status.get_name(status))
            else:
                msg.add_filename('변경없음')
            msg.end()
            infobox(msg, self)

    def init_scene_openning_set(self, sg_task, status):
        shot_name = sg_task['entity']['name']

        sv_scn_file = self.get_server_file(shot_name)

        import moon.timeline
        reload(moon.timeline)
        moon.timeline.set_fps(24)
        cmds.playbackOptions(
            edit=True,
            minTime=sg_task['entity.Shot.sg_cut_in'],
            maxTime=sg_task['entity.Shot.sg_cut_out'],
            animationStartTime=sg_task['entity.Shot.sg_cut_in'] - 2,
            animationEndTime=sg_task['entity.Shot.sg_cut_out'] + 2,
        )
        cmds.currentTime(sg_task['entity.Shot.sg_cut_in'])

        # 모델패널을 와이어프레임 상태로 변경한다.
        moon.modelpanel.to_wireframe()

        # DisplaySmoothness를 초기화한다.
        moon.clean.reset_display_smoothness()

        # 작업경로를 맞춰준다.
        ep = self.get_episode_from_shot(shot_name)
        cut = self.get_cut_from_shot(shot_name)
        sv_prj_path = dirs(pathjoin(self.get_server_ren_path(), ep, cut))
        log.debug('sv_prj_path : {}'.format(sv_prj_path))
        pm.workspace(sv_prj_path, openWorkspace=True)

        sv_scn_path = self.get_server_path(shot_name)
        set_retaining_path(sv_scn_path)

        # 최근 파일에 등록한다.
        add_recent_file(sv_scn_file)

        if status is not None:
            sg = self.get_sg_connection('admin_api')
            sg.update('Task', sg_task['id'], {'sg_status_list': status})

        self.reload_ui()

    def upload(self, sg_task, status, dialog=False, target_open=False):
        if cmds.file(query=True, modified=True):
            if dialog:
                buttons = save, ignore, cancel = '저장', '저장하지 않음', '취소'
                msg = Message(korean=True)
                msg.add('현재 씬 파일이 변경되었습니다. 저장하고 진행할까요?')
                res = questionbox(
                    parent=self,
                    message=msg,
                    icon='question',
                    button=buttons,
                    default=save,
                    cancel=cancel,
                    dismiss=cancel,
                )
                if res == cancel:
                    return
                elif res == save:
                    cmds.file(force=True, save=True)
            else:
                cmds.file(force=True, save=True)

        shot_name = sg_task['entity']['name']

        ####################################################################################################
        # 파일의 이름 정의
        ####################################################################################################
        lo_scn_file = cmds.file(query=True, sceneName=True)
        sv_scn_file = self.get_server_file(shot_name)

        ####################################################################################################
        # 로컬의 파일을 서버로 복사한다.
        ####################################################################################################
        shutil.copy(lo_scn_file, sv_scn_file)

        # sg_task의 status를 변경한다.
        sg = self.get_sg_connection('admin_api')
        data = {'sg_status_list': status}
        sg.update('Task', sg_task['id'], data)

        # # sg_version을 기록한다.
        # version_name = self.get_latest_version(sg_task)
        # data = {
        #     'project': config.sg_project,
        #     'entity': sg_task['entity'],
        #     'sg_task': sg_task,
        #     'code': version_name,
        #     'user': self.sg_login_user,
        #     'updated_by': self.sg_login_user,
        # }
        # sg_version = sg.create('Version', data)
        # print(sg_version)

        # 완료 메시지
        if dialog:
            msg = Message()
            msg.title('업로드 완료')
            msg.add('선택한 작업의 업로드가 완료되었습니다.')
            msg.add('업로드된 파일의 이름 :')
            msg.add_filename(sv_scn_file)
            msg.end()
            infobox(msg, self)

        self.reload_ui()

        if target_open:
            cmds.file(sv_scn_file, force=True, open=True)
            msg = Message()
            msg.title('주의!')
            msg.add('현재 서버 씬 파일이 열린 상태입니다.')
            msg.add('씬 파일을 저장하면 치명적인 문제가 생길 수 있습니다.')
            infobox(msg, self)

    def reload_ui(self):
        if self.last_searching_mode == 'filter':
            self.search_tasks()
        elif self.last_searching_mode == 'current':
            self.init_current_scene()

    def on_project_changed(self):
        pm.optionVar(intValue=(self.STORED_PROJECT_INDEX_OPTIONVAR, self.project_filter_combo.currentIndex()))
        self.init_episode_filter()

    def on_item_selection_changed(self):
        for btn in self.function_button_list:
            btn.disable()

        if self.work_list.is_single_selected():
            for btn in self.function_button_list:
                btn.enable()
        elif self.work_list.is_multi_selected():
            self.status_wtg_btn.enable()
            self.status_ip_btn.enable()
            self.status_fin_btn.enable()
            self.status_rrq_btn.enable()


class CopyToWindow(QDialog):

    HEADER_LABELS = ['Shot', 'Task', 'Status', 'Assigned To', 'Updated At']
    COLUMN_WIDTHS = [150, 100, 80, 120, 150]

    def __init__(self, ep, cut, sg, parent=None):
        super(CopyToWindow, self).__init__(parent)
        self.ep = ep
        self.cut = cut
        self.sg = sg
        self._ep = None
        self._cut = None
        self.parent = parent
        self.ui()

    def ui(self):
        self.setWindowTitle(self.parent.windowTitle())

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(6)

        # 씬 번호 레이아웃
        shot_name_layout = QHBoxLayout()
        shot_name_layout.setSpacing(3)

        ep_label = QLabel('Episode')
        ep_label.setFixedHeight(25)

        self.ep_field = LineEdit()
        self.ep_field.setFixedWidth(80)
        self.ep_field.setFixedHeight(25)

        cut_label = QLabel('Cut')
        cut_label.setFixedHeight(25)

        self.cut_field = LineEdit()
        self.cut_field.setFixedWidth(80)
        self.cut_field.setFixedHeight(25)

        shot_name_layout.addWidget(ep_label)
        shot_name_layout.addWidget(self.ep_field)
        shot_name_layout.addItem(QSpacerItem(30, 0))
        shot_name_layout.addWidget(cut_label)
        shot_name_layout.addWidget(self.cut_field)
        shot_name_layout.addItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        # 하단 레이아웃
        bottom_layout = QHBoxLayout()

        ok_button = Button('파일복사')
        ok_button.setFixedWidth(80)
        ok_button.clicked.connect(self.submit)

        cancel_button = Button('취소')
        cancel_button.setFixedWidth(80)
        cancel_button.clicked.connect(self.reject)

        bottom_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        bottom_layout.addWidget(ok_button)
        bottom_layout.addWidget(cancel_button)
        bottom_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addLayout(shot_name_layout)
        self.main_layout.addLayout(bottom_layout)

        self.setFixedSize(self.sizeHint())

    def submit(self):
        ep = self.ep_field.text()
        if not ep:
            return
        ep = ep.strip()
        regex = re.match(r'^\d\d$', ep)
        if not regex:
            return
        cut = self.cut_field.text()
        if not cut:
            return
        cut = cut.strip()
        regex = re.match(r'^\d\d\d[A-Z]?$', cut)
        if not regex:
            return

        if 'EP{}'.format(ep) == self.ep and 'C{}'.format(cut) == self.cut:
            errorbox('현재 열려있는 씬 파일의 이름과 같습니다.', self)
            return

        self._ep = 'EP{}'.format(ep)
        self._cut = 'C{}'.format(cut)

        self.accept()

    def get_target_info(self):
        return self._ep, self._cut


@authorized
def main():
    global hb_lighting_scene_manager_window

    try:
        hb_lighting_scene_manager_window.close()
        hb_lighting_scene_manager_window.deleteLater()
    except:
        pass

    hb_lighting_scene_manager_window = LightingSceneManagerWindow()
    hb_lighting_scene_manager_window.show()
