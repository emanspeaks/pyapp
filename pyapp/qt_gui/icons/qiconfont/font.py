from pathlib import Path

from PySide2.QtGui import QIcon, QFontDatabase

from .fontspec import CharMap
from .errors import FontError
from .sources import THIRDPARTY_FONTSPEC

IconCache = dict[str, QIcon]


class QIconFont:
    _SPECNAME: str
    _ICON_CACHE: IconCache

    @classmethod
    def get_spec(cls):
        return THIRDPARTY_FONTSPEC[cls._SPECNAME]

    def __init__(self, ttf_path: Path, charmap: CharMap):
        self.ttf_path = ttf_path
        self.charmap = charmap
        self.icon_cache = dict()

        self.load_font()

    def load_font(self):
        fontdata = self.ttf_path.read_bytes()
        id_ = QFontDatabase.addApplicationFontFromData(fontdata)
        loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)

        if loadedFontFamilies:
            self.font_id = id_
            self.font_name = loadedFontFamilies[0]
            self.font_data = fontdata
        else:
            raise FontError(
                f"Font '{self.ttf_path}' appears to be empty. "
                "If you are on Windows 10, please read "
                "https://support.microsoft.com/en-us/kb/3053676 "
                "to know how to prevent Windows from blocking "
                "the fonts that come with the package."
            )

    def get_glyph_for_codepoint(self, icon_name: str):
        return self.get_spec().charmap.get(icon_name, None)

    def get_glyph(self, name_or_codepoint: str | int):
        i = name_or_codepoint
        if isinstance(name_or_codepoint, str):
            i = self.get_glyph_for_codepoint(name_or_codepoint)
            if i is None:
                raise ValueError(f"Glyph '{name_or_codepoint}' not found "
                                 "in charmap.")
        return chr(i)

    def icon(self, *names, **kwargs):
        cache_key = f"{names}{kwargs}"
        if cache_key not in self._ICON_CACHE:
            # TODO
            i = QIcon()
            self._ICON_CACHE[cache_key] = i
            # TODO

        return self._ICON_CACHE[cache_key]
