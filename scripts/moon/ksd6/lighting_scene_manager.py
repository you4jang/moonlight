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
reload(moon.clean)
import moon.context
reload(moon.context)
import moon.modelpanel
reload(moon.modelpanel)
import moon.scriptjob
reload(moon.scriptjob)
import moon.timeline
reload(moon.timeline)
import moon.log
reload(moon.log)
import moon.shotgun
reload(moon.shotgun)
import moon.ksd6.config as config
reload(config)

import maya.cmds as cmds
import pymel.core as pm


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
        self.header_labels = ['Shot', 'Start', 'End', 'Ani\nStatus', 'Lighting\nStatus', 'Updated At']
        self.column_widths = [100, 60, 60, 120, 120, 150]

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
        self.doubleClicked.connect(self.open_work_with_dialog)

        self.header = self.horizontalHeader()
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
        # 사용자의 입력을 받아 원하는 기능을 수행하고 콜백을 보내준다.
        self._execute(self._execute_single_job_as_func, partial(self.parent.open_work))

    def contextMenuEvent(self, e, *args, **kwargs):
        super(WorkList, self).contextMenuEvent(e, *args, **kwargs)

        # 아무런 아이템도 선택되지 않으면 컨텍스트 메뉴가 보이지 않는다.
        if not self.selectedIndexes():
            return

        # 로그인 사용자의 정보가 필요하기 때문에 로그인 쿠키를 준비한다.
        self.login_sg_user = MoonLoginCookie.get_login_user().sg_user

        ####################################################################################################
        # 컨텍스트 메뉴 생성
        ####################################################################################################
        menu = QMenu(self)
        menu.setFont(MAIN_FONT)

        if self.is_single_selected():
            var = menu.addAction(QIcon(img_path('sg_logo.png')), '샷건 페이지 열기')
            var.function = self._execute_single_job_as_func
            var.callback = self.parent.open_sg_shot_page

            menu.addSeparator()

            var = menu.addAction('씬 파일 열기 (확인용)')
            var.function = self._execute_single_job_as_func
            var.callback = partial(self.parent.open_work)

            var = menu.addAction(QIcon(img_path('maya.png')), '씬 파일 열기 (작업용) >>> Doing')
            var.function = self._execute_single_job_as_func
            var.callback = partial(self.parent.open_work, status='doing')

            var = menu.addAction(QIcon(img_path('open.png')), '서버 폴더 열기')
            var.function = self._execute_single_job_as_func
            var.callback = self.parent.open_server_path

        if self.is_single_selected():
            menu.addSeparator()

            var = menu.addAction(QIcon(img_path('circle_check.png')), '상태변경 >>> In Progress')
            var.function = self._execute_multi_job_as_func
            var.callback = partial(self.parent.set_sg_status, 'doing')

            var = menu.addAction(QIcon(img_path('circle_check.png')), '상태변경 >>> Final')
            var.function = self._execute_multi_job_as_func
            var.callback = partial(self.parent.set_sg_status, 'fin')

            menu.addSeparator()

            if self.is_single_selected():
                menu.addSeparator()
                var = menu.addAction('[개발자] 디버그')
                var.function = self._execute_single_job_as_func
                var.callback = self.parent.determine_work

        # 사용자의 입력을 받아 원하는 기능을 수행하고 콜백을 보내준다.
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action:
            if hasattr(action, 'function'):
                self._execute(executer=action.function, callback=action.callback)

    def is_single_selected(self):
        return len(self.get_selected_indexes()) == 1

    def is_multi_selected(self):
        return not self.is_single_selected()

    def _get_selected_one(self):
        ranges = self.selectedRanges()
        row = ranges[0].topRow()
        return self.item(row, 0).work

    def get_selected_indexes(self):
        ranges = self.selectedRanges()
        selected = []
        for rgn in ranges:
            top_row = rgn.topRow()
            for i in range(rgn.rowCount()):
                row = top_row + i
                selected.append(row)
        return sorted(selected)

    def _get_selected(self):
        works = []
        for row in self.get_selected_indexes():
            works.append(self.item(row, 0).work)
        return works

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
        callback(self._get_selected_one(), *args, **kwargs)

    def _execute_multi_job_as_func(self, callback, *args, **kwargs):
        callback(self._get_selected(), *args, **kwargs)


class LightingSceneManagerWindow(MainWindow):

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

        # 메인 레이아웃
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setAlignment(Qt.AlignTop)

        ####################################################################################################
        # 작업 검색 그룹박스
        ####################################################################################################
        # 줄 간격 초기화 버튼
        self.clear_width_btn = IconButton('width.png', 25, 17)
        self.clear_width_btn.setToolTip('Reset width on headers.')
        self.clear_width_btn.clicked.connect(self.init_work_list_header_widths)

        self.filter_grp = Groupbox()
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_layout.setSpacing(6)

        self.episode_filter_combo = FilterCombobox(self.init_episode_filter)
        self.episode_filter_combo.setView(QListView())
        self.episode_filter_combo.setFixedSize(100, 30)
        self.episode_filter_combo.currentIndexChanged.connect(self.on_episode_changed)

        self.status_filter_combo = FilterCombobox(self.init_status_filter)
        self.status_filter_combo.setView(QListView())
        self.status_filter_combo.setFixedSize(150, 30)
        self.status_filter_combo.currentIndexChanged.connect(partial(self.on_combobox_changed, self.status_filter_combo))

        ####################################################################################################
        # 검색버튼
        ####################################################################################################
        self.search_btn = Button('검색')
        self.search_btn.setIcon(QIcon(img_path('magnifying-glass.png')))
        self.search_btn.setIconSize(QSize(12, 12))
        self.search_btn.setFixedWidth(120)
        self.search_btn.setFixedHeight(31)
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

        # 현재 열려있는 작업 검색 버튼
        open_work_btn = IconButton('target.png', 30, 17)
        open_work_btn.setToolTip('현재 열려있는 씬 파일을 찾아줍니다.')
        open_work_btn.clicked.connect(self.init_current_scene)

        self.login_picture = QLabel()
        self.login_picture.setFixedSize(25, 25)
        self.login_picture.setScaledContents(True)

        self.login_name = Label('')

        self.filter_layout.addWidget(self.clear_width_btn)
        self.filter_layout.addItem(QSpacerItem(20, 0))
        self.filter_layout.addWidget(self.episode_filter_combo)
        self.filter_layout.addWidget(self.status_filter_combo)
        self.filter_layout.addItem(QSpacerItem(20, 0))
        self.filter_layout.addWidget(self.search_btn)
        self.filter_layout.addWidget(open_work_btn)
        self.filter_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        ####################################################################################################
        # 작업리스트
        ####################################################################################################
        self.work_list_grp = QWidget()
        self.work_list_layout = QVBoxLayout(self.work_list_grp)
        self.work_list_layout.setContentsMargins(0, 0, 0, 0)
        self.work_list_layout.setAlignment(Qt.AlignTop)
        self.work_list_layout.setSpacing(6)

        # 메인 위젯
        self.work_list = WorkList(parent=self)

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
        # 레이아웃 배치
        ####################################################################################################
        self.main_layout.addLayout(self.filter_layout)
        self.main_layout.addItem(QSpacerItem(0, 12))
        self.main_layout.addWidget(self.work_list_grp)

        self.window_layout.addLayout(self.main_layout)

        restore_window(self)

        self.setMinimumHeight(500)

    def open_sg_shot_page(self, sg_task):
        sg = self.get_sg_connection('admin_apid')
        url = '{}/detail/Shot/{}'.format(sg.SHOTGUN_URL, sg_task['entity']['id'])
        os.startfile(url)

    def open_server_path(self, sg_task):
        server_path = dirs(self.get_server_path(sg_task['entity']['name']))
        open_folder(server_path)

    def init_work_list_header_widths(self):
        self.work_list.init_cell_widths()

    def init_episode_filter(self):
        log.debug('init_episode_filter()')

        self.episode_filter_combo.clear()
        self.episode_filter_combo.addItem(self.FILTER_NAME_EPISODE)

        sg = self.get_sg_connection('admin_api')
        filters = [
            ['project', 'is', config.SG_PROJECT],
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

        lgt_filters = [
            ['project', 'is', config.SG_PROJECT],
            ['step', 'is', config.SG_STEP_LIGHTING],
            ['content', 'is', 'Lighting'],
        ]

        anfx_filters = [
            ['project', 'is', config.SG_PROJECT],
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

        existing_shot_list = []

        for row, sg_task in enumerate(lgt_sg_tasks):
            shot_name = sg_task['entity']['name']
            task_name = sg_task['content']

            shot_name_item = QTableWidgetItem(shot_name)
            shot_name_item.work = sg_task
            if shot_name in existing_shot_list:
                shot_name_item.setForeground(QColor(75, 75, 75))
            else:
                existing_shot_list.append(shot_name)

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
            self.work_list.setItem(row, 3, an_status_item)
            self.work_list.setItem(row, 4, lt_status_item)
            self.work_list.setItem(row, 5, updated_item)

        # 작업을 리스트에 넣기 전에 정렬 기능을 반드시 꺼야한다.
        self.work_list.setSortingEnabled(True)

        self.count_work_list_items(len(existing_shot_list))
        self.show_latest_search_time(elapsed_time=time.time() - start_time)

        self.work_list.setEnabled(True)

    def init_filters(self):
        log.debug('init_filters()')
        self.init_episode_filter()
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

    @staticmethod
    def get_server_path(name):
        ep = name.split('_')[0]
        return dirs(pathjoin(config.SV_LGT_PATH, ep))

    @staticmethod
    def get_server_ani_path(shot_name):
        buf = shot_name.split('_')
        ep = buf[0]
        cut = buf[1]
        return pathjoin(config.SV_ANI_PATH, ep, cut, 'fdb')

    def get_server_ani_file(self, shot_name):
        buf = shot_name.split('_')
        ep = buf[0]
        cut = buf[1]
        path = self.get_server_ani_path(shot_name)
        return pathjoin(path, namejoin(ep, cut, 'fdb', 'v001.ma'))

    def get_server_file(self, name):
        path = dirs(self.get_server_path(name))
        return pathjoin(path, name + '_Lgt.mb')

    def count_work_list_items(self, shot_count=None):
        total_count = self.work_list.rowCount()
        if not shot_count:
            shot_count = total_count
        msg = [
            '<span style="color:lightgreen">샷 <b>{}</b></span>'.format(shot_count),
            '<span style="color:lightblue">태스크 <b>{}</b></span>'.format(total_count),
        ]
        self.work_count.setText(' : '.join(msg))

    def set_sg_status(self, sg_tasks, code):
        sg = self.get_sg_connection('admin_api')

        for sg_task in sg_tasks:
            data = {'sg_status_list': code}
            sg.update('Task', sg_task['id'], data)

        self.reload_ui()

    def show_latest_search_time(self, elapsed_time=None):
        message = '검색소요시간 <b>{:.02f}초</b>'.format(elapsed_time)
        self.latest_search_time.setText(message)

    @staticmethod
    def determine_work(sg_task):
        from pprint import pprint, pformat
        pprint(sg_task)

    @authorized
    def open_work(self, sg_task, status=None, complete_message=True):
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

        if os.path.isfile(sv_scn_file):
            cmds.file(
                sv_scn_file,
                force=True,
                open=True,
                prompt=False,
                ignoreVersion=True,
                preserveReferences=True,
            )
        else:
            if os.path.isfile(sv_ani_file):
                cmds.file(force=True, new=True)
                cmds.file(rename=sv_scn_file)
                cmds.file(
                    sv_ani_file,
                    reference=True,
                    namespace=':',
                    prompt=False,
                    options='v=0',
                    ignoreVersion=True,
                )
                cmds.file(force=True, save=True)
            else:
                errorbox('애니메이션 씬 파일이 없습니다.', parent=self, korean=True)
                return

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
        sv_scn_path = self.get_server_path()
        set_retaining_path(sv_scn_path)
        set_workspace(sv_scn_path)

        # 최근 파일에 등록한다.
        add_recent_file(sv_scn_file)

        if status is not None:
            sg = self.get_sg_connection('admin_api')
            sg.update('Task', sg_task['id'], {'sg_status_list': status})

        self.reload_ui()

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

    def on_episode_changed(self):
        self.on_combobox_changed(self.episode_filter_combo)

    def on_combobox_changed(self, combobox, *args):
        if combobox.currentIndex() > 0:
            combobox.setStyleSheet(QCOMBOBOX_ORANGE_STYLESHEET)
        else:
            combobox.setStyleSheet(QCOMBOBOX_STYLESHEET_ENG)
        self.work_list.clearSelection()
        self.work_list.setEnabled(False)


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
