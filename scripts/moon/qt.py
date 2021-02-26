# -*- coding: utf-8 -*-
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import __version__
from shiboken2 import wrapInstance
from moon.join import pathjoin, crjoin
from moon.config import INHOUSETOOLS_ICON_PATH
import maya.OpenMayaUI
import maya.cmds as cmds
import pymel.core as pm
import moon.scriptjob


WINDOW_TITLE = 'Moonlight'


if not pm.about(batch=True):

    def ss_size(val, qwidget=None):
        if not qwidget:
            qwidget = QWidget()
        __dpi_ratio = qwidget.logicalDpiX() / 92.0
        return val * __dpi_ratio

    ####################################################################################################
    # 주요 함수
    ####################################################################################################
    # 스타일시트 생성기
    def stylesheet(data, parent=None):
        cmd = ''
        if parent:
            cmd += parent
        for element, attributes in data.items():
            cmd += element
            cmd += ' {'
            cmd += ';'.join(attributes)
            cmd += '}\n'
        return cmd

    # 이미지 파일이름 생성기
    def _img(filename):
        return pathjoin(INHOUSETOOLS_ICON_PATH, 'qt', filename)

    ####################################################################################################
    # 스타일시트
    ####################################################################################################
    QCOMBOBOX_STYLESHEET_ENG = stylesheet({
        'QComboBox': [
            'border: 1px solid #333333',
            'border-radius: {}px'.format(ss_size(3)),
            'background-color: #5d5d5d',
        ],
        'QComboBox:enabled::hover': [
            'background-color: #707070',
        ],
        'QComboBox:disabled': [
            'border: 1px solid #373737',
            'border-radius: {}px'.format(ss_size(3)),
            'color: #373737',
            'background-color: #444444',
        ],
        'QComboBox:drop-down:enabled': [
            'width: {}px'.format(ss_size(20)),
            'subcontrol-origin: padding',
            'subcontrol-position: top right',
            'border-left-width: 1px',
            'border-left-color: #444444',
            'border-left-style: solid',
        ],
        'QComboBox:drop-down:disabled': [
            'border-left-width: 1px',
            'border-left-color: #3d3d3d',
            'border-left-style: solid',
        ],
        'QComboBox:down-arrow:enabled': [
            'image: url({})'.format(_img('QComboBox_down_arrow.png')),
        ],
        'QComboBox:down-arrow:disabled': [
            'image: url({})'.format(_img('QComboBox_down_arrow_disabled.png')),
        ],
        'QComboBox QAbstractItemView:item': [
            'height: {}px'.format(ss_size(18)),
        ],
    })

    QCOMBOBOX_STYLESHEET = stylesheet({
        'QComboBox QAbstractItemView': [
            'font-family: gulim',
            'font-size: 9pt',
        ],
    }, parent=QCOMBOBOX_STYLESHEET_ENG)

    QCOMBOBOX_ORANGE_STYLESHEET = stylesheet({
        'QComboBox': [
            'border: 1px solid orange',
        ],
    }, parent=QCOMBOBOX_STYLESHEET_ENG)

    BUTTON_STYLESHEET = stylesheet({
        'QPushButton': [
            'border-radius: 3px',
            'border: 1px solid #333333',
            'background-color: #5d5d5d',
            # 'border: 1px solid #333',
            # 'color: #111',
            # 'background-color: #E89E55',
            'padding: 0px 5px',
            'height: 22px',
        ],
        'QPushButton:enabled::hover': [
            'background-color: #707070',
        ],
        'QPushButton:enabled::pressed': [
            'background-color: #1d1d1d',
        ],
        'QPushButton:disabled': [
            'color: #373737',
            'background-color: #444444',
            'border: 1px solid #373737',
        ],
    })

    LINE_EDIT_STYLESHEET = stylesheet({
        'QLineEdit': [
            'border-radius: 3px',
            'background-color: #2b2b2b',
            'border: 1px solid #2b2b2b',
        ],
        'QLineEdit:enabled::hover': [
            'border: 1px solid #0077bb',
        ],
        'QLineEdit:enabled::focus': [
            'border: 1px solid #0077bb',
        ],
        'QLineEdit:disabled': [
            'background-color: #333333',
            'border: 1px solid #333333',
        ],
    })

    ####################################################################################################
    # 폰트
    ####################################################################################################
    # 타이틀 폰트 (한글)
    TITLE_FONT = QFont()
    TITLE_FONT.setFamily('Malgun Gothic')
    TITLE_FONT.setPointSize(14)
    TITLE_FONT.setBold(True)

    # 일반 폰트 (한글)
    MAIN_FONT = QFont()
    MAIN_FONT.setFamily('Gulim')
    MAIN_FONT.setPointSize(9)

    ####################################################################################################
    # 마야 관련 함수
    ####################################################################################################
    def maya_widget():
        """
        마야 윈도우의 포인터를 알아내
        QWidget 클래스 타입의 인스턴스를 만들어 반환한다.
        """
        maya_main_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
        return wrapInstance(long(maya_main_window_ptr), QWidget)

    def store_window(widget):
        """
        지정한 위젯의 위치와 크기를 기억하는 함수.
        restore_window를 이용하면 저장되어있는 창의 크기와 위치를
        복원할 수 있다.

        :param widget: PySide.QtGui.QDialog
        """
        geo = widget.geometry()
        if geo.width() == 0 or geo.height() == 0:
            return
        cmds.windowPref(
            widget.objectName(),
            width=geo.width(),
            height=geo.height(),
            topEdge=geo.x(),
            leftEdge=geo.y(),
        )

    def restore_window(widget, size_only=False):
        """
        지정한 위젯의 위치와 크기를 복구하는 함수.
        마야의 window.

        :param widget: PySide.QtGui.QDialog
        """
        if cmds.windowPref(widget.objectName(), exists=True):
            wh = cmds.windowPref(widget.objectName(), query=True, widthHeight=True)
            pos = cmds.windowPref(widget.objectName(), query=True, topLeftCorner=True)
            if size_only:
                x = widget.x()
                y = widget.y()
                widget.setGeometry(x, y, wh[0], wh[1])
            else:
                widget.setGeometry(pos[0], pos[1], wh[0], wh[1])

    ####################################################################################################
    # 이미지 경로 지정 함수
    ####################################################################################################
    def img_path(img):
        return pathjoin(INHOUSETOOLS_ICON_PATH, img)

    ####################################################################################################
    # 유용한 qt 위젯 관련 함수
    ####################################################################################################
    # 가로줄
    def hline():
        widget = QFrame()
        widget.setFrameShape(QFrame.HLine)
        widget.setFrameShadow(QFrame.Sunken)
        return widget

    def to_pyside(maya_ui, qt_type=QWidget):
        """
        마야용 ui 인스턴스를 pyside용 인스턴스로 변환해주는 함수.
        :param maya_ui: 마야 ui 인스턴스
        :param qt_type: 변환을 원하는 pyside 클래스 타입
        """
        ptr = maya.OpenMayaUI.MQtUtil.findControl(maya_ui)
        if ptr is None:
            ptr = maya.OpenMayaUI.MQtUtil.findLayout(maya_ui)
        if ptr is None:
            ptr = maya.OpenMayaUI.MQtUtil.findMenuItem(maya_ui)
        if ptr is not None:
            return wrapInstance(long(ptr), qt_type)
        return qt_type()

    def _none_function():
        """
        아무런 기능도 하지 않는 함수.
        보통 임시적으로 연결할 용도로 사용한다.
        """
        pass

    def disconnect(signal):
        """
        시그널의 disconnect를 간편하게 생성해주는 함수.
        """
        signal.connect(_none_function)
        signal.disconnect()

    def clear_children_in_layout(layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i).widget()
            item.setParent(None)

    class StyleSheet(object):
        """
        주어진 데이터를 이용하여 CSS 문법을 만들어낸다.
        생성자로 전달할 인자는 data로써 dict 또는 list 타입으로도 보낼 수 있다.
        해당 data의 데이터 타입을 판단하여 적절하게 변환하도록 한다.
        """

        def __init__(self, data):
            """
            반드시 data 인자를 전달받아야 한다.

            :param list or dict data: css 문법으로 만들려는 데이터
            :return str: css 문법으로 변환된 문자열
            """
            self.data = data

        def add(self, key, value):
            self.data[key] = value

        def to_string(self):
            attributes = []

            if isinstance(self.data, dict):
                for key in self.data:
                    attributes.append('{}: {}'.format(key, self.data[key]))
            elif isinstance(self.data, list):
                attributes.extend(self.data)

            # attributes 안에 내용이 있던 없던 반환한다.
            # 아무런 내용도 없으면 ';'를 반환할 것이다. 그렇다고 해도 문제가 없다. 오히려 None이 반환되는 것보다 낫다.
            return ';'.join(attributes)

    class Banner(QFrame):

        def __init__(self, title, icon=None, font=TITLE_FONT, help=None, parent=None):
            super(Banner, self).__init__(parent)
            self.help = help
            w = self.palette()
            w.setColor(self.backgroundRole(), Qt.red)
            self.setPalette(w)
            self.setStyleSheet('color:#222;background-color:#ffba00;')
            self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
            if self.help:
                self.setToolTip('더블-클릭하여 사용설명서 보기')
                self.setCursor(Qt.PointingHandCursor)

            # 메인 레이아웃
            self.main_layout = QHBoxLayout(self)
            self.main_layout.setContentsMargins(10, 10, 10, 10)
            self.main_layout.setSpacing(10)

            ####################################################################################################
            # 메인 아이콘
            ####################################################################################################
            self.main_icon = Label()
            self.main_icon.setFixedSize(32, 32)
            self.main_icon.setAlignment(Qt.AlignCenter)
            self.main_icon.setScaledContents(True)

            # 아이콘이 있으면 등록
            if icon:
                self.main_icon.setPixmap(QPixmap(img_path(icon)))
            # 없으면 앞글자만 표기
            else:
                self.main_icon.setFixedSize(20, 70)
                # self.main_icon.setText(title[0])
                # self.main_icon.setFont(TITLE_FONT)

            ####################################################################################################
            # 타이틀 및 제작사를 보여줄 레이아웃
            ####################################################################################################
            self.title_layout = QVBoxLayout()

            if not font:
                font = QFont()
                font.setFamily('Verdana')
                font.setPointSize(12)
                font.setBold(True)

            # 타이틀
            self.title = QLabel(title)
            self.title.setFont(TITLE_FONT)

            self.title_layout.addWidget(self.title)

            ####################################################################################################
            # 메인 레이아웃 배치
            ####################################################################################################
            self.main_layout.addWidget(self.main_icon)
            self.main_layout.addLayout(self.title_layout)

        def mouseDoubleClickEvent(self, *args, **kwargs):
            if self.help:
                cmds.showHelp(self.help, absolute=True)

    def _set_sizes(widget, *args):
        a = list(args)
        if isinstance(a[0], QSize):
            size = _set_qsize(widget, a[0])
            a[0] = size
        else:
            a[0] = int((widget.logicalDpiX() / 92.0) * args[0])
            a[1] = int((widget.logicalDpiY() / 92.0) * args[1])
        return tuple(a)

    def _set_size(widget, *args):
        a = list(args)
        a[0] = int((widget.logicalDpiX() / 92.0) * args[0])
        return tuple(a)

    def _set_qsize(widget, qsize):
        ratio = int((widget.logicalDpiX() / 92.0))
        qsize.setWidth(qsize.width() * ratio)
        qsize.setHeight(qsize.height() * ratio)
        return qsize

    class Button(QPushButton):

        def __init__(self, label=None, parent=None, korean=True, height=25):
            super(Button, self).__init__(label, parent)
            if korean:
                self.setFont(MAIN_FONT)
            self.setCursor(Qt.PointingHandCursor)
            if label:
                self.setText(label)
            self.setFixedHeight(25)
            self.setStyleSheet(BUTTON_STYLESHEET)

        def setFixedSize(self, *args, **kwargs):
            super(Button, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(Button, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(Button, self).setFixedHeight(*_set_size(self, *args), **kwargs)

        def setIconSize(self, qsize):
            super(Button, self).setIconSize(_set_qsize(self, qsize))

    class IconButton(Button):

        def __init__(self, path, size=None, icon_size=12, parent=None):
            super(IconButton, self).__init__(parent=parent)
            self.setIcon(QIcon(img_path(path)))
            self.setIconSize(QSize(icon_size, icon_size))
            if size:
                self.setFixedWidth(size)
                self.setFixedHeight(size)

    class MainDialog(QDialog):

        def __init__(self, window_name, parent=None):
            super(MainDialog, self).__init__(parent)
            self.win = window_name
            self.setObjectName(self.win)
            self.setFont(MAIN_FONT)
            self.setWindowTitle(WINDOW_TITLE)
            self.setWindowIcon(QIcon(QPixmap(img_path('moon_title_icon.png'))))

        def moveEvent(self, *args, **kwargs):
            store_window(self)

        def resizeEvent(self, *args, **kwargs):
            store_window(self)

        def closeEvent(self, *args, **kwargs):
            moon.scriptjob.remove_script_job(__name__)
            moon.scriptjob.remove_script_job(self.__class__.__name__)

        def setFixedSize(self, *args, **kwargs):
            super(MainDialog, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(MainDialog, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(MainDialog, self).setFixedHeight(*_set_size(self, *args), **kwargs)

    class MainWindow(QMainWindow):

        def __init__(self, parent=maya_widget()):
            super(MainWindow, self).__init__(parent)
            self.setFont(MAIN_FONT)
            self.setWindowTitle(WINDOW_TITLE)
            self.setWindowIcon(QIcon(QPixmap(img_path('moon_title_icon.png'))))

        def moveEvent(self, *args, **kwargs):
            store_window(self)

        def resizeEvent(self, *args, **kwargs):
            store_window(self)

        def setFixedSize(self, *args, **kwargs):
            super(MainWindow, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(MainWindow, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(MainWindow, self).setFixedHeight(*_set_size(self, *args), **kwargs)

    class FlowLayout(QLayout):

        def __init__(self, parent=None):
            super(FlowLayout, self).__init__(parent)
            self.setContentsMargins(9, 9, 9, 9)
            self.margin = 9
            self.setSpacing(9)
            self.space_x = 9
            self.space_y = 9
            self.itemList = []

        def __del__(self):
            item = self.takeAt(0)
            while item:
                item = self.takeAt(0)

        def addItem(self, item):
            self.itemList.append(item)

        def count(self):
            return len(self.itemList)

        def itemAt(self, index):
            if 0 <= index < len(self.itemList):
                return self.itemList[index]

        def takeAt(self, index):
            if 0 <= index < len(self.itemList):
                return self.itemList.pop(index)

        def expandingDirections(self):
            return Qt.Orientations(Qt.Orientation(0))

        def hasHeightForWidth(self):
            return True

        def heightForWidth(self, width):
            height = self.do_layout(QRect(0, 0, width, 0))
            return height

        def setGeometry(self, rect):
            super(FlowLayout, self).setGeometry(rect)
            self.do_layout(rect)

        def sizeHint(self):
            return self.minimumSize()

        def minimumSize(self):
            size = QSize()

            for item in self.itemList:
                size = size.expandedTo(item.minimumSize())

            size += QSize(self.contentsMargins().top() + self.contentsMargins().bottom(),
                          self.contentsMargins().left() + self.contentsMargins().right())
            return size

        def do_layout(self, rect):
            x = rect.x() + self.contentsMargins().left()
            y = rect.y() + self.contentsMargins().top()
            line_height = 0

            for item in self.itemList:
                next_x = x + item.sizeHint().width() + self.space_x
                if next_x - self.space_x > rect.right() - self.contentsMargins().right() and line_height > 0:
                    x = rect.x() + self.contentsMargins().left()
                    y = y + line_height + self.space_y
                    next_x = x + item.sizeHint().width() + self.space_x
                    line_height = 0

                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

                x = next_x
                line_height = max(line_height, item.sizeHint().height())

            return y + line_height - rect.y() + self.contentsMargins().bottom()

    class Combobox(QComboBox):

        def __init__(self, korean=True, *args, **kwargs):
            super(Combobox, self).__init__(*args, **kwargs)
            self.setCursor(Qt.PointingHandCursor)
            if korean:
                self.setFont(MAIN_FONT)
                self.setStyleSheet(QCOMBOBOX_STYLESHEET)
            else:
                self.setStyleSheet(QCOMBOBOX_STYLESHEET_ENG)

        @classmethod
        def toggle_highlight(cls, combobox, *args):
            if combobox.currentIndex() > 0:
                combobox.setStyleSheet(QCOMBOBOX_ORANGE_STYLESHEET)
            else:
                combobox.setStyleSheet(QCOMBOBOX_STYLESHEET_ENG)

        def setFixedSize(self, *args, **kwargs):
            super(Combobox, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(Combobox, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(Combobox, self).setFixedHeight(*_set_size(self, *args), **kwargs)

        def setMinimumSize(self, *args, **kwargs):
            super(Combobox, self).setMinimumSize(*_set_sizes(self, *args), **kwargs)

        def setMinimumWidth(self, *args, **kwargs):
            super(Combobox, self).setMinimumWidth(*_set_size(self, *args), **kwargs)

        def setMinimumHeight(self, *args, **kwargs):
            super(Combobox, self).setMinimumHeight(*_set_size(self, *args), **kwargs)

    class LineEdit(QLineEdit):

        def __init__(self, *args, **kwargs):
            super(LineEdit, self).__init__(*args, **kwargs)
            self.setStyleSheet(LINE_EDIT_STYLESHEET)

        def setFixedSize(self, *args, **kwargs):
            super(LineEdit, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(LineEdit, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(LineEdit, self).setFixedHeight(*_set_size(self, *args), **kwargs)

    class Groupbox(QGroupBox):

        def __init__(self, *args, **kwargs):
            super(Groupbox, self).__init__(*args, **kwargs)
            self.setFont(MAIN_FONT)

        def setFixedSize(self, *args, **kwargs):
            super(Groupbox, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(Groupbox, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(Groupbox, self).setFixedHeight(*_set_size(self, *args), **kwargs)

    class RadioButton(QRadioButton):

        def __init__(self, *args, **kwargs):
            super(RadioButton, self).__init__(*args, **kwargs)
            self.setCursor(Qt.PointingHandCursor)
            self.setFont(MAIN_FONT)

        def setFixedSize(self, *args, **kwargs):
            super(RadioButton, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(RadioButton, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(RadioButton, self).setFixedHeight(*_set_size(self, *args), **kwargs)

    class Label(QLabel):

        def __init__(self, text=None, korean=True, *args, **kwargs):
            super(Label, self).__init__(*args, **kwargs)
            if text:
                self.setText(text)
            if korean:
                self.setFont(MAIN_FONT)

        def setFixedSize(self, *args, **kwargs):
            super(Label, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(Label, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(Label, self).setFixedHeight(*_set_size(self, *args), **kwargs)

    class Checkbox(QCheckBox):

        def __init__(self, label=None, parent=None, *args, **kwargs):
            super(Checkbox, self).__init__(parent, *args, **kwargs)
            if label:
                self.setText(label)
            self.setFont(MAIN_FONT)

        @classmethod
        def toggle_highlight(cls, checkbox, _):
            if checkbox.isChecked():
                checkbox.setStyleSheet('color:orange;font-weight:bold')
            else:
                checkbox.setStyleSheet(None)

        def setFixedSize(self, *args, **kwargs):
            super(Checkbox, self).setFixedSize(*_set_sizes(self, *args), **kwargs)

        def setFixedWidth(self, *args, **kwargs):
            super(Checkbox, self).setFixedWidth(*_set_size(self, *args), **kwargs)

        def setFixedHeight(self, *args, **kwargs):
            super(Checkbox, self).setFixedHeight(*_set_size(self, *args), **kwargs)

    class ProgressBar(MainDialog):

        def __init__(self, maximum=100, title=None, width=500, korean=True, parent=maya_widget(),
                     visible=True):
            super(ProgressBar, self).__init__(parent)
            self.invisible = not visible
            if not visible:
                return
            self.maximum = maximum

            ####################################################################################################
            # 상수 설정
            ####################################################################################################
            self.TOTAL_LABEL = '전체' if korean else 'Total'
            self.PROG_LABEL = '현재' if korean else 'Current'
            self.PROG_INFO_LABEL = '진행정보' if korean else 'Progress Information'

            ####################################################################################################
            # 윈도우 기본설정
            ####################################################################################################
            self.setWindowTitle('Progress Window')
            self.setModal(True)

            self.window_layout = QVBoxLayout(self)
            self.window_layout.setContentsMargins(9, 9, 9, 9)
            self.window_layout.setSpacing(6)
            self.window_layout.setAlignment(Qt.AlignTop)

            ####################################################################################################
            # 메인 프레임
            ####################################################################################################
            self.main_frame = QFrame(self)
            self.main_frame.setFrameShadow(QFrame.Sunken)
            self.main_frame.setFrameShape(QFrame.Box)

            self.main_layout = QVBoxLayout(self.main_frame)
            self.main_layout.setContentsMargins(20, 20, 20, 20)
            self.main_layout.setAlignment(Qt.AlignTop)

            ####################################################################################################
            # 프로그레스 바 창의 제목
            ####################################################################################################
            self.title_label = None
            if title:
                self.title_label = Label(title)
                if korean:
                    self.title_label.setFont(TITLE_FONT)
                else:
                    font = QFont()
                    font.setPointSize(14)
                    font.setBold(True)
                    self.title_label.setFont(font)
                self.title_label.setContentsMargins(0, 0, 0, 20)

            ####################################################################################################
            # 프로그레스 바
            ####################################################################################################
            self.progbar = QProgressBar()
            self.progbar.setMinimum(0)
            self.progbar.setMaximum(maximum)
            self.progbar.setValue(0)
            self.progbar.setTextVisible(True)
            self.progbar.setAlignment(Qt.AlignCenter)
            self.progbar.setFixedHeight(15)

            # 프로그레스바의 진행상황을 알려주는 메시지
            self.proglabel = Label()

            ####################################################################################################
            # 진행정보를 알려주는 그룹박스
            ####################################################################################################
            self.info_frame = QGroupBox(self.PROG_INFO_LABEL)
            if korean:
                self.info_frame.setFont(MAIN_FONT)

            self.info_layout = QVBoxLayout(self.info_frame)
            self.info_layout.setContentsMargins(10, 20, 10, 10)

            # 전체 상태 표시
            self.total_label_layout = QHBoxLayout()
            self.total_label_layout.setSpacing(5)

            self.totalvaluelabel = Label()
            self.totalvaluelabel.setAlignment(Qt.AlignRight)
            if maximum:
                self.totalvaluelabel.setText(unicode(maximum))

            self.total_label_layout.addWidget(Label(self.TOTAL_LABEL, korean=korean))
            self.total_label_layout.addWidget(self.totalvaluelabel)

            # 현재 상태 표시
            self.prog_label_layout = QHBoxLayout()

            self.progvaluelabel = Label()
            self.progvaluelabel.setAlignment(Qt.AlignRight)

            self.prog_label_layout.addWidget(Label(self.PROG_LABEL, korean=korean))
            self.prog_label_layout.addWidget(self.progvaluelabel)

            # 그룹박스 배치
            self.info_layout.addLayout(self.total_label_layout)
            self.info_layout.addLayout(self.prog_label_layout)

            ####################################################################################################
            # 레이아웃 배치
            ####################################################################################################
            if title:
                self.main_layout.addWidget(self.title_label)
            self.main_layout.addWidget(self.progbar)
            self.main_layout.addWidget(self.proglabel)
            self.main_layout.addItem(QSpacerItem(0, 20))
            self.main_layout.addWidget(self.info_frame)

            self.window_layout.addWidget(self.main_frame)

            self.progbar.valueChanged.connect(self.disp)

            self.setFixedSize(self.sizeHint())
            self.setFixedWidth(width)
            self.show()

            self.prog(u'')

        def add_maximum(self, add):
            if add > 0:
                self.set_maximum(self.progbar.maximum() + add)

        def set_maximum(self, maximum):
            if maximum > 0:
                self.progbar.setMaximum(maximum)
                self.totalvaluelabel.setText(str(maximum))

        def prog(self, text=None):
            if self.invisible:
                return
            self.progtext = text
            self.progbar.setValue(self.progbar.value() + 1)

        def set_progress(self, progress):
            self.progbar.setValue(progress)

        def disp(self, p):
            self.progvaluelabel.setText(str(p))
            if self.progtext:
                self.proglabel.setText(self.progtext)

        def step(self):
            return self.progbar.value()

        def end(self):
            if self.invisible:
                return
            self.progbar.setValue(self.progbar.maximum())
            self.accept()

        def closeEvent(self, *args, **kwargs):
            self.deleteLater()

        def hideEvent(self, *args, **kwargs):
            self.deleteLater()

    ####################################################################################################
    # 안내문 레이블
    ####################################################################################################
    class HelpLabel(QWidget):

        def __init__(self, text, parent=None, *args, **kwargs):
            super(HelpLabel, self).__init__(parent, *args, **kwargs)
            self.main_layout = QHBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(5)

            icon = QLabel()
            icon.setPixmap(QPixmap(img_path('info.png')))
            icon.setFixedSize(12, 12)
            icon.setScaledContents(True)

            help = Label(text)
            help.setWordWrap(True)

            self.main_layout.addWidget(icon)
            self.main_layout.addWidget(help)

    ####################################################################################################
    # 텍스트 관련 함수
    ####################################################################################################
    def nice(string, fontsize=12, fontfamily=None, bold=False, lineheight='120%', indent=0, ordered=False,
             unordered=False):
        style = [
            'font-weight:{}'.format('bold' if bold else 'normal'),
            'font-size:{}px'.format(fontsize),
            'line-height:{}'.format(lineheight),
            'margin-left:{}px'.format(indent * 5)
        ]
        if fontfamily:
            style.append('font-family:{}'.format(fontfamily))
        return '<p style="{}">{}</p>'.format(';'.join(style), string)

    def highlight(text, col='#df4e4e'):
        strong_start = '<span style="color:{color}">'.format(color=col)
        strong_end = '</span>'
        return '{start}{text}{end}'.format(start=strong_start, text=text, end=strong_end)

    def mark(text, bold=False, red=False):
        buf = []
        if red:
            buf.append('<span style="color:#df4e4e">')
        if bold:
            buf.append('<b>')
        buf.append(unicode(text))
        if bold:
            buf.append('</b>')
        if red:
            buf.append('</span>')
        return '{}'.format(''.join(buf))

    def strong_different(str1, str2, bold=True, color=None, separator=''):
        """주어진 2개의 문자열을 비교하여, 바뀐 부분에 특별한 강조를 해주는 함수"""
        result = []

        comp_str1 = str1
        comp_str2 = str2

        if separator:
            comp_str1 = str1.split(separator)
            comp_str2 = str2.split(separator)

        opened = False
        for i, word in enumerate(comp_str1):
            if comp_str1[i] != comp_str2[i] and not opened:
                bold_style = ''
                color_code = ''
                if bold:
                    bold_style = 'font-weight:bold;'
                if color:
                    color_code = 'color:{}'.format(color)
                word = '<span style="{}{}">{}'.format(bold_style, color_code, comp_str2[i])
                if separator:
                    word += '</span>'
                    opened = False
                else:
                    opened = True
            elif comp_str1[i] == comp_str2[i] and opened:
                word = '</span>{}'.format(comp_str2[i])
                opened = False

            result.append(word)

        return separator.join(result)

    ####################################################################################################
    # 메시지 클래스
    ####################################################################################################
    class Message(object):

        def __init__(self, title=None, messages=None, korean=True):
            self.message_list = []
            # 영문 최적화인지 한글 최적화인지 여부
            self.korean = korean
            self.title_font = 'malgun gothic' if korean else 'arial'
            self.font = 'gulim' if korean else 'Segoe UI'
            self.fontsize = 12

            # 제목이 있으면 포함한다.
            if title:
                self.title(title)
            # 메시지가 단문이면 리스트 타입으로 변환한다.
            if isinstance(messages, unicode) or isinstance(messages, str):
                self.add(messages)
            # 메시지가 리스트면 메시지 리스트에 추가한다.
            elif isinstance(messages, list):
                self.message_list += messages
            # 메시지가 튜플이면 리스트로 변환하고 메시지 리스트에 추가한다.
            elif isinstance(messages, tuple):
                self.message_list += list(messages)

        def title(self, msg):
            self.message_list.append(nice(msg, fontsize=20, fontfamily=self.title_font, bold=True))
            return self

        def add(self, msg, indent=0, bold=False, korean=True, ordered=False, unordered=False):
            if all([ordered, unordered]):
                raise AttributeError(u"The flags both ordered and unordered can't use simultaneously.")
                return
            self.message_list.append(
                nice(msg, indent=indent, fontfamily=self.font, fontsize=self.fontsize, bold=bold, ordered=ordered, unordered=unordered))
            return self

        def add_filename(self, msg):
            self.message_list.append(nice(msg, fontsize=16, fontfamily='Consolas', indent=4))
            return self

        def br(self):
            self.message_list.append('<br/>')
            return self

        def end(self):
            self.message_list.append('<p style="line-height:0px;margin-left:400px">&nbsp;</p>')
            return self

        def output(self):
            return crjoin(*self.message_list)

    ####################################################################################################
    # 대화상자, 프롬프트, 다이얼로그 관련 함수
    ####################################################################################################
    def questionbox(parent=None, title=None, message=None, icon=None, align=None,
                    button=None, default=None, cancel=None, dismiss=None, korean=True, width=400):
        """
        메시지 상자를 만들어주는 함수

        :param parent: 부모 위젯. 없으면 마야 위젯을 지정한다.
        :param unicode title: 메시지 상자의 프레임 제목표시줄에 지정할 단어.
        :param message: 메시지 상자 안에 표시될 글.
        :param str, unicode icon: 메시지 상자 좌측에 표시할 아이콘의 형태.
        :param str align: 메시지의 정렬 지정.
        :param str, list, tuple button: 생성해야할 버튼 또는 버튼들.
        :param unicode default: 엔터키를 입력하면 실행될 기본 버튼 정의.
        :param unicode cancel: Esc나 창 닫기를 입력하면 실행될 취소 버튼 정의
        :param unicode dismiss: 창 닫기를 클릭하면 실행될 취소 버튼 정의.
        :param bool korean: 다이얼로그의 내용이 한글인지 파악하는 여부.
        :param int width: 창의 폭.
        """

        def pushbutton(btninst):
            """
            QPushButton을 생성해서 돌려준다. 반환값은 (버튼 제목, 생성된 버튼 인스턴스) 이다.

            :param btninst: 생성해야할 버튼의 이름 또는 (이름, 아이콘)
            """
            if isinstance(btninst, tuple) or isinstance(btninst, list):
                label, btnicon = btninst
            else:
                label, btnicon = btninst, None
            newbtn = Button(unicode(label))
            # newbtn.setStyleSheet('padding:7px 12px')
            newbtn.setMinimumWidth(80)
            if korean:
                newbtn.setFont(MAIN_FONT)
            if btnicon:
                pix = QIcon()
                pix.addPixmap(img_path(btnicon))
                newbtn.setIcon(pix)
                newbtn.setIconSize(QSize(20, 20))
            msgbox.addButton(newbtn, QMessageBox.YesRole)
            return label, newbtn

        buttons = {}

        if not parent:
            parent = maya_widget()

        if not title:
            title = '알림' if korean else 'Information'

        if not align:
            align = 'center'

        msgbox = QMessageBox(parent)

        if icon == 'question':
            title = '질문' if korean else 'Question'
            msgbox.setIcon(QMessageBox.Question)
        elif icon == 'warning':
            title = '경고' if korean else 'Warning'
            msgbox.setIcon(QMessageBox.Warning)
        elif icon == 'error' or icon == 'critical':
            title = '에러' if korean else 'Error'
            msgbox.setIcon(QMessageBox.Critical)
        elif icon == 'info' or icon == 'information':
            title = '알림' if korean else 'Information'
            msgbox.setIcon(QMessageBox.Information)

        # 윈도우 타이틀 정의
        msgbox.setWindowTitle(title)

        # 메시지의 타입의 Message 클래스면 unicode로 변환한다.
        if isinstance(message, Message):
            message = message.end().output()

        # msgbox.setText('<p align="{}">{}</p>'.format(align, message))
        msgbox.setText(message)

        # if korean:
        #     msgbox.setFont(MAIN_FONT)

        btnidx = 0

        if isinstance(button, tuple) or isinstance(button, list):
            for btn in button:
                b = pushbutton(btn)
                buttons[b[0]] = b[1]
                buttons[b[1]] = b[0]
                buttons[btnidx] = b[1]
                btnidx += 1
        else:
            b = pushbutton(button)
            buttons[b[0]] = b[1]
            buttons[b[1]] = b[0]
            buttons[btnidx] = b[1]
            btnidx += 1

        if default:
            msgbox.setDefaultButton(buttons[default])

        if cancel:
            msgbox.setEscapeButton(buttons[cancel])

        if dismiss:
            msgbox.setEscapeButton(buttons[dismiss])

        msgbox.setFixedWidth(width)
        msgbox.exec_()

        return buttons[msgbox.clickedButton()]

    def infobox(message, parent=None, korean=True):
        """
        정보를 제공해주는 일반적인 메시지박스

        :param message: 메시지박스에 표기할 내용
        :param korean: 한글 메시지 여부
        :param parent: 부모 위젯
        """
        btn_label = '확인' if korean else 'OK'
        return questionbox(
            parent=parent,
            title='알림' if korean else 'Information',
            message=message,
            icon='information',
            button=btn_label,
            default=btn_label,
            cancel=btn_label,
            dismiss=btn_label,
            korean=korean,
        )

    def warnbox(message, parent=None, korean=True):
        """
        경고를 알려주는 메시지박스

        :param message: 메시지박스에 표기할 내용
        :param korean: 한글 메시지 여부
        :param parent: 부모 위젯
        """
        btn_label = '확인' if korean else 'OK'
        return questionbox(
            parent=parent,
            title='경고' if korean else 'Warning',
            message=message,
            icon='warning',
            button=btn_label,
            default=btn_label,
            cancel=btn_label,
            dismiss=btn_label,
            korean=korean,
        )

    def errorbox(message, parent=None, korean=True):
        """
        치명적인 에러를 알려주는 메시지박스

        :param message: 메시지박스에 표기할 내용
        :param korean: 한글 메시지 여부
        :param parent: 부모 위젯
        """
        btn_label = '확인' if korean else 'OK'
        return questionbox(
            parent=parent,
            title='에러' if korean else 'Error',
            message=message,
            icon='critical',
            button=btn_label,
            default=btn_label,
            cancel=btn_label,
            dismiss=btn_label,
            korean=korean,
        )
