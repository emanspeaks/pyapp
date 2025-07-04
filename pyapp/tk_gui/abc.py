from tkinter import Tk, Toplevel as TkToplevel
from tkinter.ttk import Widget as TtkWidget

# constants to simplify other imports later
from tkinter import (  # noqa: F401
    TOP as tkTOP, BOTH as tkBOTH, X as tkX, Y as tkY, LEFT as tkLEFT,
    RIGHT as tkRIGHT, END as tkEND, BOTTOM as tkBOTTOM
)

from ..logging import get_logger
from ..utils.windows.funcs import set_high_dpi_support

from ..app import PyApp

from .themes import ThemeMap


# mixins

class TtkWidgetMixin(TtkWidget):
    def enable(self):
        self.configure(state='normal')

    def disable(self, emit: bool = True):
        self.configure(state='disabled')

    def get_enabled(self):
        return 'disabled' not in self.state()

    def set_enabled(self, enabled: bool, emit: bool = True):
        if enabled:
            self.enable()
        else:
            self.disable(emit)

        return enabled

    def temp_change_enabled(self, enabled: bool, emit: bool = True):
        "returns the enabled state prior to calling this function"
        current = self.get_enabled()
        self.set_enabled(enabled, emit)
        return current

    def get_tkwindow(self):
        parent = self
        while not isinstance(parent, (Tk, TkToplevel)):
            parent = parent.master
        return parent


class TkGetWindowMixin:
    def get_window(self) -> 'TkAbstractWindowWrapper':
        raise NotImplementedError('Abstract method not implemented')

    def get_window_tkroot(self):
        return self.get_window().tkroot


class TkHasViewParent(TkGetWindowMixin):
    def __init__(self, parent: TkGetWindowMixin):
        super().__init__()
        self.parent = parent


# widgets

class TkWidgetBase(TkHasViewParent):
    def __init__(self, parent: 'TkWidgetBase'):
        super().__init__()
        self.parent = parent

    def get_window(self):
        parent = self.parent
        if isinstance(parent, TkAbstractWindowWrapper):
            return parent
        return parent.get_window()


class TkWidgetWrapper(TkWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.tkroot: TtkWidget = None


class TkWindowBaseWidgetWrapper(TkWidgetWrapper):
    def __init__(self, parent: 'TkAbstractWindowWrapper'):
        super().__init__(parent)


# views

class ViewConcept:
    def __init__(self, controller: 'ViewController'):
        super().__init__()
        self.controller = controller


# windows

class TkAbstractWindowWrapper(TkGetWindowMixin, ViewConcept):
    def __init__(self, basetitle: str, controller: 'TkChildWindowController',
                 *args, **kwargs):
        super().__init__(controller)
        self.tkroot: TkToplevel = self.create_tkroot(*args, **kwargs)
        self.basewidget: TkWindowBaseWidgetWrapper = None

        self.basetitle = basetitle
        self.update_title()

    def create_tkroot(self, *args, **kwargs) -> TkToplevel:
        raise NotImplementedError('Abstract method not implemented')

    def get_window(self):
        return self

    def get_tkbasewidget(self):
        return self.basewidget.tkroot

    def update_title(self, subtitle: str = None):
        title = self.basetitle
        if subtitle:
            title += ' - ' + subtitle
        self.tkroot.title(title)

    def get_dpi(self):
        return self.tkroot.winfo_fpixels('1i')

    @property
    def hwnd(self):
        return self.tkroot.winfo_id()


class TkChildWindowWrapper(TkAbstractWindowWrapper, TkHasViewParent):
    def __init__(self, basetitle: str, controller: 'TkChildWindowController',
                 parent: TkAbstractWindowWrapper):
        TkHasViewParent.__init__(self, parent)
        TkAbstractWindowWrapper.__init__(self, basetitle, controller)

    def create_tkroot(self) -> TkToplevel:
        return TkToplevel(self.parent.get_window_tkroot())


class TkMainWindowWrapper(TkAbstractWindowWrapper):
    def __init__(self, basetitle: str, controller: 'TkApplicationBase',
                 *args, **kwargs):
        log = get_logger()
        log.debug('init main window')
        super().__init__(basetitle, controller, *args, **kwargs)

    def create_tkroot(self, *args, **kwargs) -> TkToplevel:
        ctrl: TkApplicationBase = self.controller
        return ctrl.create_tk_inst(*args, **kwargs)


# controllers

class ViewController:
    pass


class TkAbstractWindowController(TkGetWindowMixin, ViewController):
    def __init__(self):
        super().__init__()
        self.window: TkAbstractWindowWrapper = None

    def get_window(self):
        return self.window


class TkChildWindowController(TkAbstractWindowController):
    def __init__(self, parentwindow: TkAbstractWindowWrapper):
        super().__init__()
        self.window: TkChildWindowWrapper = None
        self.parentwindow = parentwindow


class TkApplicationBase(TkAbstractWindowController):
    INIT_GUI_IN_CONSTRUCTOR: bool = True

    def __init__(self, use_local: bool = False, *args, **kwargs):
        log = get_logger()
        log.debug('initializing application')
        super().__init__()
        self.themes: ThemeMap = None
        self.use_local = use_local
        self.gui_initialized = False
        self.window: TkMainWindowWrapper = None
        if self.INIT_GUI_IN_CONSTRUCTOR:
            self.init_gui(*args, **kwargs)

    def init_gui(self, *args, **kwargs):
        log = get_logger()
        log.debug('starting app main')

        set_high_dpi_support(log=log)
        self.create_main_window(*args, **kwargs)

        # we need Tk to be initialized before we can init or set themes,
        # so we wait until after the main window is created.
        self.init_themes()
        self.set_theme()

        self.gui_initialized = True

    def main(self, *args, **kwargs):
        log = get_logger()
        if not self.gui_initialized:
            self.init_gui(*args, **kwargs)

        log.debug('starting Tk main loop')
        self.get_window_tkroot().mainloop()

    def init_themes(self):
        self.themes = ThemeMap()

    def set_theme(self, t: str = None):
        log = get_logger()

        tnew = t
        t = t or PyApp['local.theme']
        log.debug(f'setting theme to {t}')
        if tnew:
            PyApp.set('local.theme', t)

        self.themes.apply_theme(t)

    def get_theme(self):
        return self.themes.get_current_theme()

    def create_tk_inst(self, *args, **kwargs):
        return Tk()

    def create_main_window(self, *args, **kwargs) -> TkMainWindowWrapper:
        "sets self.window to an instance of the concrete main window object"
        raise NotImplementedError('Abstract method not implemented')
