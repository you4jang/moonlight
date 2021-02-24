# -*- coding: utf-8 -*-
from mv.qt import *
from functools import partial
import mv.shotgun


def fore_color(value):
    if value is None:
        return 200
    return value


def back_color(value):
    if value is None:
        return 43
    return value


class StatusListWidget(QTableWidget):
    HEADER_LABELS = ['Name', 'Code', 'Icon', 'Fore R', 'Fore G', 'Fore B', 'Back R', 'Back G', 'Back B']
    COLUMN_WIDTHS = [100, 60, 40, 40, 40, 40, 40, 40, 40]
    OV_PREFIX = 'moon_shotgun_status_manager_list_widget_header_optionvar'

    def __init__(self, parent=None):
        super(StatusListWidget, self).__init__(parent)
        self.parent = parent

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        self.setCornerButtonEnabled(False)
        self.setWordWrap(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.header = self.horizontalHeader()
        self.header.setStretchLastSection(False)

        self.init_header()

    def init(self):
        self.init_header()
        self.setRowCount(0)
        self.setSortingEnabled(True)

    def init_header(self):
        self.setColumnCount(len(self.HEADER_LABELS))
        self.setHorizontalHeaderLabels(self.HEADER_LABELS)
        for i, title in enumerate(self.HEADER_LABELS):
            width = self.COLUMN_WIDTHS[i]
            self.setColumnWidth(i, width)


class ShotgunStatusManagerWindow(MainDialog):

    def __init__(self, parent=maya_widget()):
        self.win = 'moon_shotgun_status_manager_window'
        super(ShotgunStatusManagerWindow, self).__init__(self.win, parent)
        self.setObjectName(self.win)
        self.setWindowTitle('HeroBooks - Asset Manager')

        self.window_layout = QVBoxLayout(self)
        self.window_layout.setAlignment(Qt.AlignTop)

        self.work_list = StatusListWidget(parent=self)

        self.window_layout.addWidget(self.work_list)

        restore_window(self)
        self.search_tasks()

    def search_tasks(self, asset_code=None, task=None, clear=False, ignore_filter=False):
        self.work_list.init()

        # 단순히 리스트만 초기화하고 싶을 때는 실행을 종료한다.
        if clear:
            return

        sg = self.get_sg_connection('admin_api')
        filters = []
        fields = [
            'name',
            'code',
            'sg_maya_foreground_r',
            'sg_maya_foreground_g',
            'sg_maya_foreground_b',
            'sg_maya_background_r',
            'sg_maya_background_g',
            'sg_maya_background_b',
        ]
        order = [
            {'field_name': 'code', 'direction': 'asc'},
        ]
        sg_status = sg.find('Status', filters, fields, order)

        self.work_list.setSortingEnabled(False)

        # 작업의 개수를 파악하여 row를 생성한다.
        row_count = len(sg_status)
        self.work_list.setRowCount(row_count)

        for row, status in enumerate(sg_status):
            fr = fore_color(status['sg_maya_foreground_r'])
            fg = fore_color(status['sg_maya_foreground_g'])
            fb = fore_color(status['sg_maya_foreground_b'])
            br = back_color(status['sg_maya_background_r'])
            bg = back_color(status['sg_maya_background_g'])
            bb = back_color(status['sg_maya_background_b'])

            name_item = QTableWidgetItem(status['name'])
            name_item.setForeground(QColor(fr, fg, fb))
            name_item.setBackground(QColor(br, bg, bb))

            code_item = QTableWidgetItem(status['code'])
            icon_item = QTableWidgetItem()
            icon_item.setIcon(QIcon(img_path('sg_status/{}.png'.format(status['code']))))
            fr_item = QTableWidgetItem(str(fr))
            fg_item = QTableWidgetItem(str(fg))
            fb_item = QTableWidgetItem(str(fb))
            br_item = QTableWidgetItem(str(br))
            bg_item = QTableWidgetItem(str(bg))
            bb_item = QTableWidgetItem(str(bb))

            self.work_list.setItem(row, 0, name_item)
            self.work_list.setItem(row, 1, code_item)
            self.work_list.setItem(row, 2, icon_item)
            self.work_list.setItem(row, 3, fr_item)
            self.work_list.setItem(row, 4, fg_item)
            self.work_list.setItem(row, 5, fb_item)
            self.work_list.setItem(row, 6, br_item)
            self.work_list.setItem(row, 7, bg_item)
            self.work_list.setItem(row, 8, bb_item)

        # 작업을 리스트에 넣기 전에 정렬 기능을 반드시 꺼야한다.
        self.work_list.setSortingEnabled(True)

    def get_sg_connection(self, name):
        if not hasattr(self, 'sg_connections'):
            self.sg_connections = {}
        if name not in self.sg_connections:
            sg = mv.shotgun.Shotgun(name)
            self.sg_connections[name] = sg
        return self.sg_connections[name]


def window():
    global mv_sg_status_manager_win

    try:
        mv_sg_status_manager_win.close()
        mv_sg_status_manager_win.deleteLater()
    except:
        pass

    mv_sg_status_manager_win = ShotgunStatusManagerWindow()
    mv_sg_status_manager_win.show()
