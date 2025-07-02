from .abc import TkApplicationBase

_APP: TkApplicationBase = None


def get_app():
    return _APP


def get_mainwindow():
    return get_app().window


def get_main_tk():
    return get_app().get_window_tkroot()


def register(*args, **kwargs):
    return get_main_tk().register(*args, **kwargs)


def idle():
    get_main_tk().update_idletasks()
