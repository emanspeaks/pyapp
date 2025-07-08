from pathlib import Path

from pyapp import PyApp

from .logging import log_func_call

HERE = Path(__file__).parent


class IconBrowserApp(PyApp):
    APP_NAME: str = 'IconBrowser'
    APP_LOG_PREFIX = 'IconBrowser'
    APP_ASSETS_DIR = HERE/"assets"

    @classmethod
    @log_func_call
    def main(cls, input_data: dict | str | Path = None, *args,
             **kwargs):
        cls.init_main(input_data, True, **kwargs)

        from .gui import IconBrowserGui
        gui = IconBrowserGui(args)
        cls.gui = gui
        return gui.main(*args, **kwargs)

    @classmethod
    @log_func_call
    def preprocess_args(cls, args: list[str]):
        return args
