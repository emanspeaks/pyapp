from ..logging import log_func_call
from .abc import TkApplicationBase

_APP: TkApplicationBase = None


@log_func_call
def get_app():
    return _APP


@log_func_call
def get_mainwindow():
    return get_app().window


@log_func_call
def get_main_tk():
    return get_app().get_window_tkroot()


@log_func_call
def register(*args, **kwargs):
    return get_main_tk().register(*args, **kwargs)


@log_func_call
def idle():
    get_main_tk().update_idletasks()
