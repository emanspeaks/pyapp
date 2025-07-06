from pathlib import Path

from PySide2.QtGui import QIcon, QFontDatabase

from ....logging import log_func_call, DEBUGLOW2
from .fontspec import CharMap
from .errors import QIconFontError
from .sources import THIRDPARTY_FONTSPEC

IconCache = dict[str, QIcon]


class QIconFont:
    _SPECNAME: str
    _ICON_CACHE: IconCache

    @classmethod
    @log_func_call(DEBUGLOW2)
    def get_spec(cls):
        return THIRDPARTY_FONTSPEC[cls._SPECNAME]

    @log_func_call
    def __init__(self, ttf_path: Path, charmap: CharMap):
        self.ttf_path = ttf_path
        self.charmap = charmap
        self.icon_cache = dict()

        self.load_font()

    @log_func_call
    def load_font(self):
        fontdata = self.ttf_path.read_bytes()
        id_ = QFontDatabase.addApplicationFontFromData(fontdata)
        loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)

        if loadedFontFamilies:
            self.font_id = id_
            self.font_name = loadedFontFamilies[0]
            self.font_data = fontdata
        else:
            raise QIconFontError(
                f"Font '{self.ttf_path}' appears to be empty. "
                "If you are on Windows 10, please read "
                "https://support.microsoft.com/en-us/kb/3053676 "
                "to know how to prevent Windows from blocking "
                "the fonts that come with the package."
            )

    @log_func_call
    def get_glyph_for_codepoint(self, icon_name: str):
        return self.get_spec().charmap.get(icon_name, None)

    @log_func_call
    def get_glyph(self, name_or_codepoint: str | int):
        i = name_or_codepoint
        if isinstance(name_or_codepoint, str):
            i = self.get_glyph_for_codepoint(name_or_codepoint)
            if i is None:
                raise ValueError(f"Glyph '{name_or_codepoint}' not found "
                                 "in charmap.")
        return chr(i)

    # TODO this is only for now for testing, it should be an instance method
    @classmethod
    @log_func_call
    def icon(cls, *names, **kwargs):
        cache_key = f"{names}{kwargs}"
        if cache_key not in cls._ICON_CACHE:
            # TODO
            i = QIcon()
            cls._ICON_CACHE[cache_key] = i
            # TODO

        return cls._ICON_CACHE[cache_key]
