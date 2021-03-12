# -*- coding: utf-8 -*-
from moon.authentication import *
from moon.qt import *
import os


class EdlEditorWindow(MainDialog):

    LAST_DIR_OPTIONVAR = 'ksd6_edl_editor_window_last_dir_optionvar'

    def __init__(self, parent=maya_widget()):
        super(EdlEditorWindow, self).__init__('ksd6_edl_editor_window', parent)
        self.ui()

    def ui(self):
        self.setWindowTitle('ksd6 - EDL Editor')
        self.setObjectName('ksd6_edl_editor_window')
        self.setMinimumSize(300, 500)

        self.window_layout = QVBoxLayout(self)
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(0)
        self.window_layout.setAlignment(Qt.AlignTop)

        self.banner = QLabel()
        self.banner.setPixmap(QPixmap(img_path('ksd6/banner.png')))
        self.banner.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.window_layout.addWidget(self.banner)
        self.window_layout.addWidget(hline())

        ####################################################################################################
        # 메인 레이아웃
        ####################################################################################################
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.window_layout.addLayout(self.main_layout)

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

        btn_layout = QHBoxLayout()
        execute_btn = Button('실행')
        execute_btn.setFixedWidth(100)
        execute_btn.setFixedHeight(30)
        execute_btn.clicked.connect(self.execute)
        btn_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        btn_layout.addWidget(execute_btn)
        btn_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.main_layout.addLayout(btn_layout)

        restore_window(self)
        self.restore_file_path()

    def browse_path(self):
        last_dir = self.path_field.text()
        if last_dir == '':
            pm.optionVar(query=self.LAST_DIR_OPTIONVAR)
        sel = QFileDialog.getExistingDirectory(
            parent=self,
            caption='EDL 파일이 있는 곳을 선택하세요',
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
            if not f.endswith('.edl'):
                continue
            self.file_list_widget.addItem(f)
        self.file_list_widget.sortItems()

    def execute(self):
        path = self.path_field.text()
        edl = self.file_list_widget.selectedItems()
        if not edl:
            return
        for e in edl:
            edl_file = e.text()
            edl_path = pathjoin(path, edl_file)

            with open(edl_path) as f:
                data = f.read()

            with open(edl_path, 'w') as f:
                for line in data.split('\n'):
                    if line.startswith('*'):
                        shot = line.split(':')[-1].split('.')[0]
                        f.write(line.replace(line, line + '\n*%s\n' % shot))
                    else:
                        f.write(line)
                        f.write('\n')
        infobox('작업을 완료하였습니다', self)


@authorized
def main():
    global ksd6_edl_editor_win

    try:
        ksd6_edl_editor_win.close()
        ksd6_edl_editor_win.deleteLater()
    except:
        pass

    ksd6_edl_editor_win = EdlEditorWindow()
    ksd6_edl_editor_win.show()
