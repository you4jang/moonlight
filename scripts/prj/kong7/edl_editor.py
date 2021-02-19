# -*- coding: utf-8 -*-
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
    from shiboken2 import wrapInstance
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from shiboken import wrapInstance

import os
import sys

TOOLS_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(TOOLS_PATH, 'icons/')


class EdlEditorWindow(QDialog):

    def __init__(self, parent=None):
        super(EdlEditorWindow, self).__init__(self, parent)
        self.ui()

        self.btn_logo.setIcon(QIcon(ICON_PATH + 'cadet_logo.png'))
        self.btn_logo.setIconSize(QSize(55, 40))

        self.tb_dir.clicked.connect(self.selectDir)
        self.btn_run.clicked.connect(self.run)

        self.line_path.editingFinished.connect(self.get_list)

    def ui(self):
        self.setMinimumSize(300, 500)
        self.setWindowTitle('EDL Editor')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)

        self.window_layout = QVBoxLayout(self.centralwidget)
        self.window_layout.setAlignment(Qt.AlignTop)

        ####################################################################################################
        # mid_layout
        ####################################################################################################
        self.mid_grp = QGroupBox()
        
        self.mid_layout = QVBoxLayout()
        self.mid_layout.setAlignment(Qt.AlignTop)
        self.mid_layout.setContentsMargins(0, 0, 0, 0)

        self.groupBox_2 = QGroupBox()
        self.groupBox_2.setTitle("")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setContentsMargins(-1, 15, -1, -1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 10)
        self.line_path = QLineEdit(self.groupBox_2)
        self.horizontalLayout.addWidget(self.line_path)

        self.tb_dir = QToolButton('...')
        self.horizontalLayout.addWidget(self.tb_dir)

        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.lw_list = QListWidget(self.groupBox_2)
        self.lw_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lw_list.setMovement(QListView.Static)
        self.lw_list.setResizeMode(QListView.Fixed)
        self.lw_list.setLayoutMode(QListView.SinglePass)
        self.lw_list.setViewMode(QListView.ListMode)
        self.lw_list.setModelColumn(0)
        self.verticalLayout_3.addWidget(self.lw_list)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.mid_layout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox('Edit')
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setContentsMargins(-1, 15, -1, -1)
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setContentsMargins(-1, -1, -1, 0)

        self.btn_run = QPushButton('Run')
        self.verticalLayout_6.addWidget(self.btn_run)
        self.verticalLayout_5.addLayout(self.verticalLayout_6)
        self.mid_layout.addWidget(self.groupBox)
        self.window_layout.addLayout(self.mid_layout)

        self.lb_log = QLabel(self.centralwidget)
        self.lb_log.setText("")
        self.lb_log.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.window_layout.addWidget(self.lb_log)

        ####################################################################################################
        # 레이아웃
        ####################################################################################################
        self.window_layout.addLayout(self.top_layout)

        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

    def selectDir(self):
        self.line_path.setText(QFileDialog.getExistingDirectory())
        self.get_list()

    def get_list(self):
        self.lw_list.clear()
        file_path = self.line_path.text()
        file_list = []
        if not file_path:
            return
        for x in os.listdir(file_path):

            if x.endswith('.edl'):
                file_list.append(x)
                QListWidget.addItem(self.lw_list, x)

    def run(self):
        path = self.line_path.text()
        edl = self.lw_list.selectedItems()

        for e in edl:
            edlfile = e.text()
            edlPath = os.path.join(path, edlfile)

            with open(edlPath, 'r') as f:
                data = f.read()
            f.close()
            with open(edlPath, "w") as fd:
                # lines = data.readlines()
                for line in data.split('\n'):
                    if line.startswith('*'):
                        shot = line.split(':')[-1].split('.')[0]
                        fd.write(line.replace(line, line + '\n*%s\n' % shot))
                    else:
                        fd.write(line)
                        fd.write('\n')
            fd.close()
            print '%s completed' % edlPath


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = EdlEditorWindow()
    w.show()
    sys.exit(app.exec_())
