from PySide2.QtWidgets import QMainWindow, QWidget, QApplication
from PySide2.QtGui import QPalette, QColor

from ..logging import get_logger, log_func_call
from ..app import PyApp
# from ..utils.windows import set_high_dpi_support

STATUS_LABEL = 'status_label'  # used in stylesheet for status label


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

    @log_func_call
    def get_qtwindow(self):
        parent = self
        while not isinstance(parent, (QMainWindow, QApplication)):
            parent = parent.parent()
        return parent


class QtGetWindowMixin:
    @log_func_call
    def get_window(self) -> 'QtWindowWrapper':
        raise NotImplementedError('Abstract method not implemented')

    @log_func_call
    def get_window_qtroot(self):
        return self.get_window().qtroot


class QtHasViewParent(QtGetWindowMixin):
    @log_func_call
    def __init__(self, parent: QtGetWindowMixin):
        QtGetWindowMixin.__init__(self)
        self.parent = parent


# widgets

class QtWidgetBase(QtHasViewParent):
    @log_func_call
    def __init__(self, parent: 'QtWidgetBase'):
        QtHasViewParent.__init__(self, parent)
        # self.parent = parent

    @log_func_call
    def get_window(self):
        parent = self.parent
        if isinstance(parent, QtWindowWrapper):
            return parent
        return parent.get_window()


class QtWidgetWrapper(QtWidgetBase):
    @log_func_call
    def __init__(self, parent: QtWidgetBase):
        QtWidgetBase.__init__(self, parent)
        self.qtroot: QWidget = None


class QtWindowBaseWidgetWrapper(QtWidgetWrapper):
    @log_func_call
    def __init__(self, parent: 'QtWindowWrapper'):
        QtWidgetWrapper.__init__(self, parent)


# views

class ViewConcept:
    @log_func_call
    def __init__(self, controller: 'ViewController'):
        self.controller = controller


# windows

class QtWindowWrapper(QtGetWindowMixin, ViewConcept):
    @log_func_call
    def __init__(self, basetitle: str, controller: 'QtChildWindowController',
                 *args, **kwargs):
        QtGetWindowMixin.__init__(self)
        ViewConcept.__init__(self, controller)

        qtroot = self.create_qtroot(*args, **kwargs)
        self.qtroot = qtroot

        basewidget = self.create_basewidget()
        self.basewidget = basewidget
        qtroot.setCentralWidget(basewidget.qtroot)

        self.basetitle = basetitle
        self.update_title()

    @log_func_call
    def create_qtroot(self, *args, **kwargs) -> QMainWindow:
        return QMainWindow(*args, **kwargs)

    @log_func_call
    def create_basewidget(self) -> QtWindowBaseWidgetWrapper:
        raise NotImplementedError('Abstract method not implemented')

    @log_func_call
    def get_window(self):
        return self

    @log_func_call
    def get_qtbasewidget(self):
        return self.basewidget.qtroot

    @log_func_call
    def update_title(self, subtitle: str = None):
        title = self.basetitle
        if subtitle:
            title += ' - ' + subtitle

        self.qtroot.setWindowTitle(title)

    @log_func_call
    def get_dpi(self):
        return self.qtroot.devicePixelRatio()

    @property
    def hwnd(self):
        return self.qtroot.winId()

    @log_func_call
    def show(self):
        self.qtroot.show()


class QtChildWindowWrapper(QtHasViewParent, QtWindowWrapper):
    @log_func_call
    def __init__(self, basetitle: str, controller: 'QtChildWindowController',
                 parent: QtWindowWrapper):
        QtHasViewParent.__init__(self, parent)
        QtWindowWrapper.__init__(self, basetitle, controller)


# class QtMainWindowWrapper(QtAbstractWindowWrapper):
#     def __init__(self, basetitle: str, controller: 'QtApplicationBase',
#                  *args, **kwargs):
#         log = get_logger()
#         log.debug('init main window')
#         super().__init__(basetitle, controller)
#         # self.qtroot = controller.create_qt_inst(*args, **kwargs)


# controllers

class ViewController:
    pass


class QtWindowController(ViewController, QtGetWindowMixin):
    @log_func_call
    def __init__(self):
        ViewController.__init__(self)
        QtGetWindowMixin.__init__(self)
        self.window: QtWindowWrapper = None

    @log_func_call
    def get_window(self):
        return self.window


class QtChildWindowController(QtWindowController):
    @log_func_call
    def __init__(self, parentwindow: QtWindowWrapper):
        QtWindowController.__init__(self)
        self.window: QtChildWindowWrapper = None
        self.parentwindow = parentwindow


class QtApplicationBase:
    INIT_GUI_IN_CONSTRUCTOR: bool = True

    @log_func_call
    def __init__(self, app_args: list[str], *firstwin_args, **firstwin_kwargs):
        log = get_logger()
        log.debug('initializing application')
        self.gui_initialized = False
        self.qtroot: QApplication = None
        self.windows: list[QtWindowWrapper] = list()
        if self.INIT_GUI_IN_CONSTRUCTOR:
            self.init_gui(app_args, *firstwin_args, **firstwin_kwargs)

    @log_func_call
    def init_gui(self, app_args: list[str], *firstwin_args, **firstwin_kwargs):
        log = get_logger()
        log.debug('starting app main')
        self.qtroot = self.create_qt_inst(app_args)

        # set_high_dpi_support(log=log)
        self.create_first_window(*firstwin_args, **firstwin_kwargs)

        # we need Qt to be initialized before we can init or set themes,
        # so we wait until after the main window is created.
        self.init_themes()
        self.set_theme()

        self.gui_initialized = True

    @log_func_call
    def main(self, *args, **kwargs):
        log = get_logger()
        if not self.gui_initialized:
            self.init_gui(*args, **kwargs)

        log.debug('starting Qt main loop')
        self.qtroot.exec_()

    @log_func_call
    def init_themes(self):
        pass

    @log_func_call
    def set_theme(self, t: str = None):
        log = get_logger()

        tnew = t
        t = t or PyApp['local.theme']
        log.debug(f'setting theme to {t}')
        if tnew:
            PyApp.set('local.theme', t)

        app = self.qtroot
        if t.lower() == "dark":
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
            app.setPalette(palette)
            # Enhanced dark style for toolbar button hover
            app.setStyleSheet(f'''
                QToolBar QToolButton {{
                    background: transparent;
                    color: #fff;
                    border: none;
                    padding: 4px 8px;
                }}
                QToolBar QToolButton:hover {{
                    background: #444a5a;
                    color: #fff;
                    border-radius: 4px;
                }}
                QToolBar QToolButton:pressed {{
                    background: #2a82da;
                    color: #fff;
                }}
                QLabel#{STATUS_LABEL} {{
                    padding: 2px 8px;
                    background: #444a5a;
                    color: #fff;
                    border-radius: 4px;
                }}
                QLabel#{STATUS_LABEL}:hover {{
                    background: #2a82da;
                    color: #fff;
                }}
                QToolTip {{
                    color: #ffffff;
                    background-color: #2a82da;
                    border: 1px solid white;
                }}
            ''')
        else:
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet('')

    @log_func_call
    def get_theme(self):
        pass
        # return self.themes.get_current_theme()

    @log_func_call
    def create_qt_inst(self, app_args: list[str] = []):
        return QApplication(list(app_args))

    @log_func_call
    def create_first_window(self, *args, **kwargs) -> QtWindowWrapper:
        "create and show the first window after app launch"
        raise NotImplementedError('Abstract method not implemented')
