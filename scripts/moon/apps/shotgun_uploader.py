# -*- coding: utf-8 -*-
from moon.authentication import *
from moon.join import *
from moon.path import *
from moon.qt import *
from functools import partial
import re
import moon.shotgun
reload(moon.shotgun)
import pymel.core as pm


class ShotgunUploaderWindow(MainDialog):

    LAST_DIR_OPTIONVAR = 'ksd6_shotgun_uploader_window_last_dir_optionvar'
    STORED_PROJECT_INDEX_OPTIONVAR = 'shotgun_uploader_stored_project_index_optionvar'

    def __init__(self, parent=maya_widget()):
        super(ShotgunUploaderWindow, self).__init__('ksd6_shotgun_uploader_window', parent)
        self.ui()

    def ui(self):
        self.setWindowTitle('Shotgun Uploader')
        self.setObjectName('ksd6_shotgun_uploader_window')
        self.setMinimumSize(400, 500)

        self.window_layout = QVBoxLayout(self)
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(0)
        self.window_layout.setAlignment(Qt.AlignTop)

        ####################################################################################################
        # 메인 레이아웃
        ####################################################################################################
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.window_layout.addLayout(self.main_layout)

        # 프로젝트 선택
        self.project_filter_combo = Combobox(korean=False)
        self.project_filter_combo.setView(QListView())
        self.project_filter_combo.setFixedHeight(25)
        self.init_project_filter()
        self.main_layout.addWidget(self.project_filter_combo)
        self.main_layout.addItem(QSpacerItem(0, 20))

        path_layout = QHBoxLayout()
        reload_btn = IconButton('reload.png', 25, 17)
        reload_btn.clicked.connect(self.init_file_list)
        path_layout.addWidget(reload_btn)
        self.path_field = LineEdit()
        self.path_field.setFixedHeight(25)
        self.path_field.setReadOnly(True)
        self.browse_btn = Button('...', korean=False)
        self.browse_btn.setFixedSize(50, 25)
        self.browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_field)
        path_layout.addWidget(self.browse_btn)
        self.main_layout.addLayout(path_layout)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list_widget.setSortingEnabled(True)
        self.file_list_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.file_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_layout.addWidget(self.file_list_widget)

        task_layout = QHBoxLayout()
        self.task_checkbox = Label('저장할 태스크')
        task_layout.addWidget(self.task_checkbox)
        self.task_combo = Combobox(korean=False)
        self.task_combo.setView(QListView())
        self.task_combo.setFixedHeight(25)
        self.task_combo.addItem('Layout')
        self.task_combo.addItem('Animation')
        self.task_combo.addItem('Lighting')
        self.task_combo.addItem('FX')
        task_layout.addWidget(self.task_combo)
        self.main_layout.addLayout(task_layout)

        status_layout = QHBoxLayout()
        self.status_checkbox = Label('저장할 상태')
        status_layout.addWidget(self.status_checkbox)
        self.status_combo = Combobox(korean=False)
        self.status_combo.setView(QListView())
        self.status_combo.setFixedHeight(25)
        self.status_combo.addItem('Pending Review')
        self.status_combo.addItem('Final')
        status_layout.addWidget(self.status_combo)
        self.main_layout.addLayout(status_layout)

        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedHeight(15)
        self.main_layout.addWidget(self.prog_bar)

        upload_layout = QHBoxLayout()
        upload_all_btn = Button('전체 업로드')
        upload_all_btn.setFixedHeight(25)
        upload_all_btn.clicked.connect(self.upload)
        upload_layout.addWidget(upload_all_btn)
        upload_sel_btn = Button('선택한 것만 업로드')
        upload_sel_btn.setFixedHeight(25)
        upload_sel_btn.clicked.connect(partial(self.upload, selected=True))
        upload_layout.addWidget(upload_sel_btn)
        self.main_layout.addLayout(upload_layout)

        restore_window(self)
        self.restore_file_path()

    def init_project_filter(self):
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
        self.project_filter_combo.clear()
        for i, sg_prj in enumerate(project_list):
            self.project_filter_combo.addItem(sg_prj['name'])
            self.project_filter_combo.setItemData(i, sg_prj)
        if pm.optionVar(exists=self.STORED_PROJECT_INDEX_OPTIONVAR):
            idx = pm.optionVar(query=self.STORED_PROJECT_INDEX_OPTIONVAR)
            self.project_filter_combo.setCurrentIndex(idx)

    def browse_path(self):
        last_dir = self.path_field.text()
        if last_dir == '':
            pm.optionVar(query=self.LAST_DIR_OPTIONVAR)
        sel = QFileDialog.getExistingDirectory(
            parent=self,
            caption='영상 파일이 있는 곳을 선택하세요',
            dir=last_dir,
            options=QFileDialog.ShowDirsOnly,
        )
        if sel:
            self.set_destination_path(sel)

    def set_destination_path(self, path):
        old_path = ''
        if pm.optionVar(exists=self.LAST_DIR_OPTIONVAR):
            old_path = pm.optionVar(query=self.LAST_DIR_OPTIONVAR)
        if not os.path.isdir(path):
            errorbox('존재하지 않는 폴더입니다.', self)
            self.path_field.setText(old_path)
            return
        self.path_field.setText(path)
        pm.optionVar(stringValue=(self.LAST_DIR_OPTIONVAR, path))
        self.init_file_list()

    def restore_file_path(self):
        if pm.optionVar(exists=self.LAST_DIR_OPTIONVAR):
            self.path_field.setText(pm.optionVar(query=self.LAST_DIR_OPTIONVAR))
            self.init_file_list()

    def init_file_list(self):
        path = self.path_field.text()
        if path is None or path == '':
            return
        self.file_list_widget.clear()
        for f in os.listdir(path):
            regex = re.match(r'^(KSD6|KS7)_EP\d\d_C\d\d\d[A-Z]?', f, re.IGNORECASE)
            if not regex:
                continue
            if not f.endswith(('.mov', '.mp4')):
                continue
            self.file_list_widget.addItem(f)
        self.file_list_widget.sortItems()

    def get_sg_connection(self, name):
        if not hasattr(self, 'sg_connections'):
            self.sg_connections = {}
        if name not in self.sg_connections:
            sg = moon.shotgun.Shotgun(name)
            self.sg_connections[name] = sg
        return self.sg_connections[name]

    def upload(self, selected=False):
        if selected:
            sel = self.file_list_widget.selectedItems()
        else:
            sel = []
            for i in range(self.file_list_widget.count()):
                sel.append(self.file_list_widget.item(i))
        if not sel:
            return
        sg = self.get_sg_connection('admin_api')
        path = self.path_field.text()
        task = self.task_combo.currentText()
        status = self.status_combo.currentText()
        if status == 'Pending Review':
            status_code = 'rev'
        elif status == 'Final':
            status_code = 'fin'
        else:
            return
        valid_files = []
        for s in sel:
            filename = s.text()
            regex = re.match(r'^(KSD6|KS7)_(?P<ep>EP\d\d)_(?P<cut>C\d\d\d[A-Z]?)', filename, re.IGNORECASE)
            if not regex:
                continue
            ep = regex.group('ep')
            cut = regex.group('cut')
            valid_files.append((filename, ep, cut))
        self.prog_bar.reset()
        self.prog_bar.setMaximum(len(valid_files))
        sg_prj = self.get_selected_sg_project()
        for filename, ep, cut in valid_files:
            self.prog_bar.setValue(self.prog_bar.value() + 1)
            shot_name = namejoin(ep, cut)
            filters = [
                ['project', 'is', sg_prj],
                ['code', 'is', shot_name],
            ]
            sg_shot = sg.find_one('Shot', filters)

            filters = [
                ['project', 'is', sg_prj],
                ['content', 'is', task],
                ['entity', 'is', sg_shot],
            ]
            sg_task = sg.find_one('Task', filters)
            sg.update('Task', sg_task['id'], {'sg_status_list': status_code})

            login_user = MoonLoginCookie.get_login_user().sg_user
            data = {
                'project': sg_prj,
                'entity': sg_shot,
                'sg_task': sg_task,
                'code': basenameex(filename),
                'user': login_user,
                'updated_by': login_user,
            }
            sg_version = sg.create('Version', data)
            sg.upload('Version', sg_version['id'], pathjoin(path, filename), 'sg_uploaded_movie')
        self.prog_bar.reset()

    def get_server_root_path(self):
        idx = self.project_filter_combo.currentIndex()
        if idx == 0:
            path = pathjoin('K:', 'KongsuniDance6')
        else:
            path = pathjoin('K:', 'Kongsuni7')
        return path

    def get_selected_sg_project(self):
        idx = self.project_filter_combo.currentIndex()
        return self.project_filter_combo.itemData(idx)


@authorized
def main():
    global ksd6_shotgun_uploader_win

    try:
        ksd6_shotgun_uploader_win.close()
        ksd6_shotgun_uploader_win.deleteLater()
    except:
        pass

    ksd6_shotgun_uploader_win = ShotgunUploaderWindow()
    ksd6_shotgun_uploader_win.show()

