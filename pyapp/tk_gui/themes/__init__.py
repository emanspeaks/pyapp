from tkinter.ttk import Style

from ...logging import log_func_call
from .dark import dark_theme

_sty = None


class ThemeMap:
    PREFS_BTN_COLOR_DEFAULT = 'medium slate blue'
    PREFS_BTN_STYLE_DEFAULT = 'PrefsDefault.TButton'

    PREFS_BTN_COLOR_LOCAL = 'sienna2'
    PREFS_BTN_STYLE_LOCAL = 'PrefsLocal.TButton'

    CANCEL_BTN_COLOR = "burlywood1"
    CANCEL_BTN_STYLE = 'Cancel.TButton'

    SAVE_BTN_COLOR = "DarkSeaGreen1"
    SAVE_BTN_STYLE = 'Save.TButton'

    _custom_themes = set()

    @staticmethod
    @log_func_call
    def get_global_style():
        global _sty
        if not _sty:
            _sty = Style()

        return _sty

    @log_func_call
    def __init__(self):
        if not self._custom_themes:
            self.init_themes()

    @classmethod
    @log_func_call
    def create_theme(cls, name: str, base: str = 'vista'):
        themes = cls._custom_themes
        if name not in themes:
            s = cls.get_global_style()
            s.theme_create(name, base)
            s.theme_use(name)
            themes.add(name)

    @classmethod
    @log_func_call
    def init_themes(cls):
        # create Light alias for vista
        cls.create_theme('Light', 'alt')

        # create Dark theme based on equilux
        cls.create_theme('Dark', 'alt')
        dark_theme(cls.get_global_style())

    @classmethod
    @log_func_call
    def apply_theme(cls, name: str):
        cls.get_global_style().theme_use(name)
        cls.apply_custom_button_themes()

    @classmethod
    @log_func_call
    def apply_custom_button_themes(cls):
        s = cls.get_global_style()

        # ttk does not support 3D buttons by default
        s.configure('TLabelframe', relief='groove')
        # s.configure('TLabelframe', borderwidth=1)
        s.configure('TButton', relief='raised')  # , borderwidth=5)
        s.map(
            'TButton',
            # background=[
            #     ('active', '#e0e0e0'),  # Lighter color when active
            #     ('!active', '#f0f0f0'),  # Default face color
            # ],
            relief=[
                ('pressed', 'sunken'),
                ('!pressed', 'raised')
            ],
        )

        s.configure('PrefsLocal.TButton',
                    background=cls.PREFS_BTN_COLOR_LOCAL,
                    foreground='black')
        s.configure('PrefsDefault.TButton',
                    background=cls.PREFS_BTN_COLOR_DEFAULT,
                    foreground='black')
        s.configure('Save.TButton',
                    background=cls.SAVE_BTN_COLOR,
                    foreground='black')
        s.configure('Cancel.TButton',
                    background=cls.CANCEL_BTN_COLOR,
                    foreground='black')

    @classmethod
    @log_func_call
    def get_current_theme(cls):
        return cls.get_global_style().theme_use(None)

    @classmethod
    @log_func_call
    def list_themes(cls):
        return cls.get_global_style().theme_names()
