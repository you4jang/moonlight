# -*- coding: utf-8 -*-
from functools import wraps
from datetime import datetime
from moon.qt import *
import os
import urllib
import cPickle
import moon.log
import moon.shotgun
reload(moon.shotgun)


__all__ = [str(x) for x in ['authorized', 'show_window', 'MoonLoginCookie']]


_REMEMBER_ID_STATE_OPTIONVAR = 'login_remember_id_state'
_REMEMBER_ID_OPTIONVAR = 'login_remember_id'
_REMEMBER_ACCOUNT_OPTIONVAR = 'login_remember_account_state'


log = moon.log.get_logger('moon.authentication')


def authorized(callback):

    @wraps(callback)
    def wrapper(*args, **kwargs):

        execute = False

        if MoonLoginCookie.exists():
            execute = True
        else:
            global moonloggedwin
            global moonloginwin

            try:
                moonloggedwin.close()
                moonloggedwin.deleteLater()
            except:
                pass

            try:
                moonloginwin.close()
                moonloginwin.deleteLater()
            except:
                pass

            moonloginwin = MoonLoginWindow(auth=True)
            result = moonloginwin.exec_()

            if result:
                execute = True

        if execute:
            return callback(*args, **kwargs)

    return wrapper


@authorized
def show_window():
    global moonloggedwin

    try:
        moonloggedwin.close()
        moonloggedwin.deleteLater()
    except:
        pass

    moonloggedwin = MoonLoggedWindow()
    moonloggedwin.show()


class MoonLoginWindow(MainDialog):

    win = 'moon_login_window'

    def __init__(self, callback=None, auth=False):
        super(MoonLoginWindow, self).__init__(self.win, parent=maya_widget())
        self.result = False
        self.callback = callback
        self.authentication = auth
        self.ui()

    def ui(self):
        self.setObjectName(self.win)
        self.setWindowTitle('문 로그인')

        self.window_layout = QVBoxLayout(self)
        self.window_layout.setContentsMargins(5, 5, 5, 5)
        self.window_layout.setSpacing(5)

        ####################################################################################################
        # 메인 레이아웃 생성
        ####################################################################################################
        self.main_widget = QFrame()
        self.main_widget.setFrameShape(QFrame.Box)
        self.main_widget.setFrameShadow(QFrame.Sunken)

        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(Qt.AlignTop)

        # 타이틀
        self.title = Label('문 로그인')
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(TITLE_FONT)

        self.title_icon = QLabel()
        self.title_icon.setPixmap(img_path('moon_title_icon.png'))

        ####################################################################################################
        # 아이디, 패스워드 필드 생성
        ####################################################################################################
        self.id_field = LineEdit()
        self.id_field.setFixedHeight(30)
        self.id_field.setStyleSheet('padding: 5px')
        self.id_field.setPlaceholderText('아이디')

        self.pw_field = LineEdit()
        self.pw_field.setFixedHeight(30)
        self.pw_field.setStyleSheet('padding: 5px')
        self.pw_field.setEchoMode(QLineEdit.Password)
        self.pw_field.setPlaceholderText('비밀번호')

        self.remember_field = Checkbox('아이디 기억하기')
        self.remember_field.stateChanged.connect(self.on_remember_id_changed)

        self.login_btn = Button('로그인')
        self.login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_btn.clicked.connect(self.on_submit)
        self.login_btn.setFixedHeight(30)

        self.id_field.returnPressed.connect(self.on_submit)
        self.pw_field.returnPressed.connect(self.on_submit)

        ####################################################################################################
        # 배치
        ####################################################################################################
        self.main_layout.addWidget(self.title)
        self.main_layout.addItem(QSpacerItem(0, 20))
        self.main_layout.addWidget(self.id_field)
        self.main_layout.addWidget(self.pw_field)
        self.main_layout.addWidget(self.login_btn)
        self.main_layout.addItem(QSpacerItem(0, 10))
        self.main_layout.addWidget(self.remember_field)

        self.window_layout.addWidget(self.main_widget)

        ####################################################################################################
        # 윈도우 크기, 위치
        ####################################################################################################
        restore_window(self)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())
        self.setFixedWidth(300)
        self.show()

        ####################################################################################################
        # 스타트업 메소드
        ####################################################################################################
        self._init_optionvar()

    def _init_optionvar(self):
        if cmds.optionVar(exists=_REMEMBER_ID_STATE_OPTIONVAR):
            value = cmds.optionVar(query=_REMEMBER_ID_STATE_OPTIONVAR)
            if value:
                self.remember_field.setChecked(True)
                if cmds.optionVar(exists=_REMEMBER_ID_OPTIONVAR):
                    user_id = cmds.optionVar(query=_REMEMBER_ID_OPTIONVAR)
                    if user_id:
                        self.id_field.setText(user_id)
                        self.pw_field.setFocus()
        # self.remember_account_field.setChecked(False)

    @staticmethod
    def _check_login(member_id, password):
        sg = moon.shotgun.Shotgun('admin_api')

        filters = [
            ['login', 'is', member_id]
        ]

        fields = [
            'image',
            'name',
            'sg_status_list',
            'login',
            'department',
            'groups',
            'email',
            'permission_rule_set',
        ]

        sg_user = sg.find_one('HumanUser', filters, fields)
        if not sg_user:
            return

        if sg.authenticate_human_user(member_id, password):
            return sg_user

    @staticmethod
    def on_remember_id_changed(state):
        value = True if state == 2 else False
        cmds.optionVar(intValue=(_REMEMBER_ID_STATE_OPTIONVAR, value))

    @staticmethod
    def on_remember_account_changed(state):
        value = True if state == 2 else False
        cmds.optionVar(intValue=(_REMEMBER_ACCOUNT_OPTIONVAR, value))

    def on_submit(self):
        user_id = self.id_field.text()
        password = self.pw_field.text()

        if not user_id or not password:
            msg = Message()
            msg.title('입력 오류')
            msg.add('아이디 또는 비밀번호를 입력하세요.')
            msg.end()
            errorbox(msg, self)
            return

        try:
            user_id.encode('ascii')
            password.encode('ascii')
        except UnicodeEncodeError:
            msg = Message()
            msg.title('문자 에러')
            msg.add('아이디나 암호는 한글을 입력할 수 없습니다.')
            msg.end()
            errorbox(msg.output(), parent=self)
            return

        sg_user = self._check_login(user_id, password)

        if not sg_user:
            self.pw_field.clear()
            msg = Message()
            msg.title('계정 오류')
            msg.add('존재하지 않는 계정입니다.')
            msg.end()
            errorbox(msg.output(), parent=self)
            return

        # 로그인 쿠키를 생성한다.
        MoonLoginCookie.create(sg_user)

        # 아이디를 기억하는 기능이 켜져 있다면 해당 아이디를 마야의 optionvar에 저장한다.
        if cmds.optionVar(exists=_REMEMBER_ID_STATE_OPTIONVAR):
            if cmds.optionVar(query=_REMEMBER_ID_STATE_OPTIONVAR):
                cmds.optionVar(stringValue=(_REMEMBER_ID_OPTIONVAR, user_id))

        self.accept()


class MoonLoggedWindow(MainDialog):

    win = 'logged_window'

    class InformationLabel(Label):

        def __init__(self, parent=None):
            super(MoonLoggedWindow.InformationLabel, self).__init__(parent)
            self.setFixedHeight(25)

    class InfomationField(LineEdit):

        def __init__(self, korean=False, parent=None):
            super(MoonLoggedWindow.InfomationField, self).__init__(parent)
            self.setReadOnly(True)
            self.setFixedHeight(25)
            if korean:
                self.setFont(MAIN_FONT)

    def __init__(self):
        super(MoonLoggedWindow, self).__init__(self.win, parent=maya_widget())
        self.setObjectName(self.win)
        self.setWindowTitle('문 로그인')

        # 메인 윈도우의 레이아웃 설정
        self.window_layout = QVBoxLayout(self)
        self.window_layout.setContentsMargins(5, 5, 5, 5)
        self.window_layout.setSpacing(5)

        ####################################################################################################
        # 메인 레이아웃 생성
        ####################################################################################################
        self.main_widget = QFrame()
        self.main_widget.setFrameShape(QFrame.Box)
        self.main_widget.setFrameShadow(QFrame.Sunken)

        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignTop)

        # 썸네일
        self.picture_field = QLabel()
        self.picture_field.setFixedSize(300, 300)
        self.picture_field.setScaledContents(True)
        self.picture_field.setStyleSheet('border: 1px solid #333')

        # 정보패널
        self.info_layout = QFormLayout()
        self.info_layout.setSpacing(3)
        self.info_layout.setHorizontalSpacing(6)

        self.user_id_field = self.InfomationField()
        self.email_field = self.InfomationField()

        self.info_layout.addRow(self.InformationLabel('아이디'), self.user_id_field)
        self.info_layout.addRow(Label('이메일'), self.email_field)

        logout_layout = QHBoxLayout()
        self.logout_btn = Button('로그아웃')
        self.logout_btn.setFixedSize(100, 30)
        self.logout_btn.clicked.connect(self.process_logout)
        logout_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        logout_layout.addWidget(self.logout_btn)
        logout_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        # 메인 레이아웃 배치
        self.main_layout.addWidget(self.picture_field)
        self.main_layout.addItem(QSpacerItem(0, 20))
        self.main_layout.addLayout(self.info_layout)
        self.main_layout.addItem(QSpacerItem(0, 20))
        self.main_layout.addLayout(logout_layout)
        self.window_layout.addWidget(self.main_widget)

        # 윈도우 설정
        restore_window(self)
        self.adjustSize()

        # 필드 입력
        self.initialize_profile()

    def set_thumbnail(self, url=None):
        pixmap = QPixmap()
        if url:
            image_data = urllib.urlopen(url).read()
            pixmap.loadFromData(image_data)
        else:
            pixmap.load(img_path('no_image_300_300.png'))
        self.picture_field.setPixmap(pixmap)

    def initialize_profile(self):
        sg_user = MoonLoginCookie.get_login_user().sg_user

        self.user_id_field.setText(sg_user['login'])
        self.set_thumbnail(sg_user['image'])
        self.email_field.setText(sg_user['email'])

    def process_logout(self):
        MoonLoginCookie.delete()
        self.close()
        self.deleteLater()
        pm.evalDeferred(show_window)


class MoonLoginCookie(object):

    def __init__(self):
        super(MoonLoginCookie, self).__init__()

    @classmethod
    def filename(cls):
        return pathjoin(os.environ['temp'], 'logincookie')

    @classmethod
    def exists(cls):
        if os.path.isfile(cls.filename()):
            modified_time = datetime.fromtimestamp(os.path.getmtime(cls.filename()))
            sub = datetime.now() - modified_time

            # 로그인 쿠키 접근이 없을 때 자동으로 쿠키를 삭제하는 시간.
            cutoff = 60 * 60 * 8

            if cutoff < sub.seconds:
                os.remove(cls.filename())
                return

            return True

    @classmethod
    def create(cls, user_data):
        c = MoonLoginUser(user_data)
        with open(cls.filename(), 'w') as f:
            cPickle.dump(c, f, protocol=2)

    @classmethod
    def delete(cls):
        if cls.exists():
            os.remove(cls.filename())

    @classmethod
    def get_login_user(cls):
        if not os.path.isfile(cls.filename()):
            return

        with open(cls.filename()) as f:
            have_to_remove = False
            try:
                user = cPickle.load(f)
            except ValueError:
                have_to_remove = True
            except ImportError:
                have_to_remove = True
            except AttributeError:
                have_to_remove = True

            if have_to_remove:
                cls.delete()
                return

            return user


class MoonLoginUser(object):

    def __init__(self, sg_user=None):
        self.sg_user = sg_user
        self.user_id = None
        self.name = None
        self.team = None
        self.image = None
        self.is_supervisor = None

        if sg_user:
            self.user_id = sg_user['login']
            self.name = sg_user['name']
            self.team = sg_user['department']
            self.image = sg_user['image']
            self.email = sg_user['email'] if 'email' in sg_user else None


class DescriptionLabel(QLabel):
    
    def __init__(self, default_text):
        super(DescriptionLabel, self).__init__(None)
        self._default_text = default_text
        self.default()

    def _set_text(self, text):
        self.setText('* {}'.format(text))

    def default(self):
        self._set_text(self._default_text)
        self.setStyleSheet(None)

    def confirm(self, text):
        self._set_text(text)
        self.setStyleSheet('color: lightgreen')

    def error(self, text):
        self._set_text(text)
        self.setStyleSheet('color: #f44')


class InputField(LineEdit):
    
    def __init__(self, callback=None, korean=False, width=None, password=False, *args, **kwargs):
        super(InputField, self).__init__(*args, **kwargs)
        self._valid = False
        if korean:
            self.setFont(MAIN_FONT)
        if width:
            self.setFixedWidth(width)
        self.setFixedHeight(25)
        if callback:
            self.editingFinished.connect(callback)
        if password:
            self.setEchoMode(self.Password)

    def set(self, state):
        self._valid = state

    def valid(self):
        return self._valid
