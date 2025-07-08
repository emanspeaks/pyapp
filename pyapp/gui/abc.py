from PySide2.QtWidgets import (
    QMainWindow, QWidget, QApplication, QDialog, QSplashScreen, QProgressBar,
    QLabel
)
from PySide2.QtCore import qVersion, Qt, QRect
from PySide2.QtGui import QPixmap, QMouseEvent, QPalette

from ..logging import get_logger, log_func_call, DEBUGLOW2, DEBUG
from ..app import PyApp
from ..config.keys import LOCAL_CFG_KEY

from .notify import ExcHandlingQApp
from .qrc import compile_qrc, import_qrc
from .themes import ThemeMap
from .themes import STATUS_LABEL  # noqa: F401
from .loadstatus import load_status_step, splash_message, LOAD_STEP_REGISTRY


@log_func_call(DEBUGLOW2, trace_only=True)
def get_gui_app() -> 'QtApplicationBase':
    global QT_APP_INST
    if not QT_APP_INST:
        raise RuntimeError("Qt application instance is not initialized.")
    return QT_APP_INST


@log_func_call(DEBUGLOW2, trace_only=True)
def get_qt_app() -> QApplication:
    app = get_gui_app()
    if app:
        return app.qtroot


# mixins

class QtWidgetMixin(QWidget):
    @log_func_call
    def enable(self):
        self.setEnabled(True)

    @log_func_call
    def disable(self, emit: bool = True):
        self.setEnabled(False)

    @log_func_call
    def set_enabled(self, enabled: bool, emit: bool = True):
        if enabled:
            self.enable()
        else:
            self.disable(emit)

        return enabled

    @log_func_call
    def temp_change_enabled(self, enabled: bool, emit: bool = True):
        "returns the enabled state prior to calling this function"
        current = self.isEnabled()
        self.set_enabled(enabled, emit)
        return current

    @log_func_call(DEBUGLOW2, trace_only=True)
    def get_qtwindow(self):
        parent = self
        while not isinstance(parent, (QMainWindow, QApplication,
                                      ExcHandlingQApp)):
            parent = parent.parent()
        return parent


class QtGetWindowMixin:
    @log_func_call
    def get_window(self) -> 'QtWindowWrapperBase':
        raise NotImplementedError('Abstract method not implemented')

    @log_func_call(DEBUGLOW2, trace_only=True)
    def get_window_qtroot(self):
        return self.get_window().qtroot


class QtHasViewParent(QtGetWindowMixin):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, parent: QtGetWindowMixin):
        QtGetWindowMixin.__init__(self)
        self.parent = parent


# widgets

class QtWidgetBase(QtHasViewParent):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, parent: 'QtWidgetBase'):
        QtHasViewParent.__init__(self, parent)
        # self.parent = parent

    @log_func_call(DEBUGLOW2, trace_only=True)
    def get_window(self):
        parent = self.parent
        if isinstance(parent, QtWindowWrapper):
            return parent
        return parent.get_window()


class QtWidgetWrapper(QtWidgetBase):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, parent: QtWidgetBase):
        QtWidgetBase.__init__(self, parent)
        self.qtroot: QWidget = None


class QtWindowBaseWidgetWrapper(QtWidgetWrapper):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, parent: 'QtWindowWrapper'):
        QtWidgetWrapper.__init__(self, parent)


# views

class ViewConcept:
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, controller: 'ViewController'):
        self.controller = controller


# windows

class QtWindowWrapperBase(QtGetWindowMixin):
    @log_func_call
    def show(self):
        self.qtroot.show()

    @log_func_call(DEBUGLOW2, trace_only=True)
    def get_window(self):
        return self

    @log_func_call
    def __init__(self, *args, **kwargs):
        QtGetWindowMixin.__init__(self)
        qtroot = self.create_qtroot(*args, **kwargs)
        self.qtroot = qtroot

    @log_func_call(DEBUGLOW2, trace_only=True)
    def create_qtroot(self, *args, **kwargs) -> QWidget:
        raise NotImplementedError('Abstract method not implemented')

    @property
    def hwnd(self):
        return self.qtroot.winId()

    @log_func_call
    def bring_to_front(self):
        qtroot = self.qtroot
        qtroot.raise_()
        qtroot.activateWindow()
        qtroot.showNormal()


class QtSplashScreen(QtWindowWrapperBase):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def create_qtroot(self, pixmap: QPixmap = None,
                      flags: Qt.WindowFlags = Qt.WindowStaysOnTopHint,
                      *args, **kwargs):
        return QSplashScreen(pixmap or QPixmap(), flags, *args, **kwargs)

    def mousePressEvent(self, event: QMouseEvent):
        # Prevent the splash from being closed by mouse click
        pass

    @log_func_call(DEBUG)
    def __init__(self, pixmap: QPixmap = None, *args,
                 text: str = "Loading...", **kwargs):
        QtWindowWrapperBase.__init__(self, pixmap or QPixmap(),
                                     Qt.WindowStaysOnTopHint)
        self.qtroot: QSplashScreen
        qtroot = self.qtroot
        qtroot.mousePressEvent = self.mousePressEvent

        rect = pixmap.rect() if pixmap else QRect(0, 0, 400, 400)

        gridsize = 20

        pb = QProgressBar(qtroot)
        pb.setGeometry(gridsize, round((rect.height() + gridsize)*0.75),
                       rect.width() - 2*gridsize, gridsize)
        pb.setRange(0, len(LOAD_STEP_REGISTRY) or 1)
        pb.setValue(0)
        pb.setStyleSheet('''
            QProgressBar {
                background-color: #19232D;
                border: 1px solid #455364;
                color: #DFE1E2;
                border-radius: 4px;
                text-align: center;
            }

            QProgressBar:disabled {
                background-color: #19232D;
                border: 1px solid #455364;
                color: #788D9C;
                border-radius: 4px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #346792;
                color: #19232D;
                border-radius: 4px;
            }

            QProgressBar::chunk:disabled {
                background-color: #26486B;
                color: #788D9C;
                border-radius: 4px;
            }
        ''')
        self.progress = pb

        lbl = QLabel(qtroot)
        lbl.setGeometry(gridsize, round((rect.height() - gridsize)*0.75),
                        rect.width() - 2*gridsize, gridsize)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setText(text)
        palette = lbl.palette()
        palette.setColor(QPalette.Window, lbl.palette().color(QPalette.Window))
        lbl.setAutoFillBackground(True)
        lbl.setPalette(palette)
        self.label = lbl

    @log_func_call(DEBUGLOW2, trace_only=True)
    def set_progress(self, *, value: int = None, message: str = None,
                     process_events: bool = True):
        progress = self.progress
        mymax = progress.maximum()
        refresh = mymax // 200 or 1
        process_events = process_events and ((message and value is None)
                                             or (value
                                                 and value % refresh == 0)
                                             or value == mymax
                                             or value == 0
                                             )

        if value is not None:
            progress.setValue(value)

        if message:
            self.label.setText(message)
            # self.qtroot.showMessage(message,
            #                         Qt.AlignBottom | Qt.AlignHCenter,
            #                         Qt.white)

        if process_events:
            QApplication.processEvents()


class QtDialogWrapper(QtWindowWrapperBase, ViewConcept):
    @log_func_call
    def __init__(self, basetitle: str, controller: 'QtChildWindowController',
                 *args, **kwargs):
        QtWindowWrapperBase.__init__(self, *args, **kwargs)
        ViewConcept.__init__(self, controller)
        self.qtroot: QDialog

        self.basetitle = basetitle
        self.update_title()

    @log_func_call(DEBUGLOW2, trace_only=True)
    def create_qtroot(self, *args, **kwargs):
        return QDialog(*args, **kwargs)

    @log_func_call
    def update_title(self, subtitle: str = None):
        title = self.basetitle
        if subtitle:
            title += ' - ' + subtitle

        self.qtroot.setWindowTitle(title)

    @log_func_call
    def get_dpi(self):
        return self.qtroot.devicePixelRatio()


class QtWindowWrapper(QtDialogWrapper):
    @log_func_call
    def __init__(self, basetitle: str, controller: 'QtWindowController',
                 *args, **kwargs):
        QtDialogWrapper.__init__(self, basetitle, controller, *args, **kwargs)
        ViewConcept.__init__(self, controller)
        self.qtroot: QMainWindow
        qtroot = self.qtroot
        basewidget = self.create_basewidget()
        self.basewidget = basewidget
        qtroot.setCentralWidget(basewidget.qtroot)

    @log_func_call(DEBUGLOW2, trace_only=True)
    def create_qtroot(self, *args, **kwargs) -> QMainWindow:
        return QMainWindow(*args, **kwargs)

    @log_func_call
    def create_basewidget(self) -> QtWindowBaseWidgetWrapper:
        raise NotImplementedError('Abstract method not implemented')

    @log_func_call(DEBUGLOW2, trace_only=True)
    def get_qtbasewidget(self):
        return self.basewidget.qtroot


class QtChildWindowWrapper(QtHasViewParent, QtWindowWrapper):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, basetitle: str, controller: 'QtChildWindowController',
                 parent: QtWindowWrapper):
        QtHasViewParent.__init__(self, parent)
        QtWindowWrapper.__init__(self, basetitle, controller)


# controllers

class ViewController:
    pass


class QtWindowController(ViewController, QtGetWindowMixin):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self):
        ViewController.__init__(self)
        QtGetWindowMixin.__init__(self)
        self.window: QtWindowWrapper = None

    @log_func_call
    def get_window(self):
        return self.window

    @log_func_call
    def show(self):
        self.window.show()


class QtDialogController(QtWindowController):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, parentwindow: QtWindowWrapper):
        QtWindowController.__init__(self)
        self.window: QtDialogWrapper = None
        self.parentwindow = parentwindow


class QtChildWindowController(QtDialogController):
    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, parentwindow: QtWindowWrapper):
        QtDialogController.__init__(self, parentwindow)
        self.window: QtChildWindowWrapper = None


class QtApplicationBase:
    INIT_GUI_IN_CONSTRUCTOR: bool = True

    @log_func_call(DEBUGLOW2, trace_only=True)
    def __init__(self, app_args: list[str], *firstwin_args, **firstwin_kwargs):
        log = get_logger()
        log.debug('initializing application')
        global QT_APP_INST
        if QT_APP_INST is not None:
            raise RuntimeError(
                "A Qt application instance already exists for this Python "
                "process. Only one instance is allowed per Python process."
            )
        QT_APP_INST = self
        self.gui_initialized = False

        self.qtroot: QApplication = None
        self.themes: ThemeMap = None
        self.windows: list[QtWindowWrapper] = list()
        self.splash: QtSplashScreen = None
        self.loading_step_registry = set()
        self.completed_load_steps = set()
        if self.INIT_GUI_IN_CONSTRUCTOR:
            self.init_gui(app_args, *firstwin_args, **firstwin_kwargs)

    @property
    def qtapp(self):
        return self.qtroot

    @log_func_call
    def create_splash(self, *args, **kwargs) -> QtSplashScreen:
        return QtSplashScreen(QPixmap(), *args, **kwargs)

    @log_func_call
    @load_status_step("GUI initialized", show_step_done=True,
                      show_step_start=False)
    def init_gui(self, app_args: list[str], *firstwin_args, **firstwin_kwargs):
        log = get_logger()
        log.debug('starting app main')

        # NOTE: this is not really used anymore since I am using qdarkstyle,
        # but wanted to keep the code for reference since I may have a need
        # later on to use Qt resource files.
        #
        # Ensure Qt resources are registered before any widgets are created
        compile_qrc()
        import_qrc()

        app = self.create_qt_inst(app_args)
        self.qtroot = app
        PyApp.set('Qt_version', qVersion())
        self.init_themes()
        self.set_theme()

        splash = self.create_splash()
        if splash:
            splash.show()
            app.processEvents()
            self.splash = splash

        from .icons.iconfont import init_iconfonts
        init_iconfonts()
        # set_high_dpi_support(log=log)
        self.create_first_window(*firstwin_args, **firstwin_kwargs)
        self.gui_initialized = True

    @log_func_call
    def main(self, *args, **kwargs):
        log = get_logger()
        if not self.gui_initialized:
            self.init_gui(*args, **kwargs)

        log.debug('starting Qt main loop')
        splash_message("Main loop starting")
        self.qtroot.exec_()

    @log_func_call
    def init_themes(self):
        self.themes = ThemeMap(self.qtroot)

    @log_func_call
    def set_theme(self, t: str = None):
        log = get_logger()

        tnew = t
        t = t or PyApp[f'{LOCAL_CFG_KEY}.theme']
        log.debug(f'setting theme to {t}')
        if tnew:
            PyApp.set(f'{LOCAL_CFG_KEY}.theme', t)

        self.themes.apply_theme(t)

    @log_func_call
    def get_theme(self):
        return self.themes.get_current_theme()

    @log_func_call
    def create_qt_inst(self, app_args: list[str] = []):
        return ExcHandlingQApp(list(app_args))

    @log_func_call
    def create_first_window(self, *args, **kwargs) -> QtWindowWrapper:
        "create and show the first window after app launch"
        raise NotImplementedError('Abstract method not implemented')

    @log_func_call
    def close_splash(self, delegate: QWidget = None):
        if self.splash:
            qtsplash: QSplashScreen = self.splash.get_window_qtroot()
            qtsplash.finish(delegate)
            self.splash = None


QT_APP_INST: QtApplicationBase | None = None
