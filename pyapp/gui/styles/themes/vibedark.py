from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path

from ....logging import log_func_call
from ...qt import QPalette, QColor
if TYPE_CHECKING:
    from ...gui_app import QtApp

from ....utils.encoding import read_text_utf8
# from ...icons.iconfont.icon import IconSpec
# from ....utils.json import load_jsonc
# from ...utils import qicon_to_data_uri
# from ..qss import merge_qss_properties

ASSETS_DIR = Path(__file__).parent.parent / "assets"


@log_func_call
def vibedark(app: QtApp):
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
    # Supplement missing roles from dark()
    palette.setColor(QPalette.Light, QColor(180, 180, 180))
    palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    palette.setColor(QPalette.Dark, QColor(35, 35, 35))
    palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    palette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))
    # Disabled state roles
    palette.setColor(QPalette.Disabled, QPalette.WindowText,
                     QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                     QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                     QColor(127, 127, 127))

    # qss_file = ASSETS_DIR/"vibedark.qss"
    qss_file = ASSETS_DIR/"vibedark.qss"
    qss = read_text_utf8(qss_file)
    # qss = merge_qss_icons(qss)

    # qss_dump = PyApp.mkdir_temp()/'vibedark-full.qss'
    # qss_dump.write_text(qss, encoding='utf-8')

    app.style().unpolish(app)
    app.setStyle("Fusion")
    app.setPalette(palette)
    app.setStyleSheet(qss)


# def _create_icon_for_theme(fontspec_name: str, icon_name: str):
#     """Create QIcon for themed proxy style."""
#     ispec = IconSpec.generate_iconspec(fontspec_name, glyph_name=icon_name)
#     return ispec.icon()

# BEWARE: this does not work because QSS does not reliably support using
# data URIs for icons.  This approach was abandoned.
#
# @log_func_call
# def merge_qss_icons(qss: str):
#     icon_json = ASSETS_DIR/"vibedark-icons.json"
#     icon_map = load_jsonc(icon_json)
#     size = QSize(16, 16)
#     for css_selector, icon_data in icon_map.items():
#         ispec = IconSpec.generate_iconspec(icon_data['fontspec_name'],
#                                            glyph_name=icon_data['icon_name'])
#         icon_uri = qicon_to_data_uri(ispec.icon(), size)
#         if not icon_uri.startswith("data:image/png;base64,"):
#             raise ValueError("invalid icon URI format, "
#                              "expected PNG data URI")

#         # # Remove font-based properties that conflict with bitmap images
#         updates = {"image": f'url("{icon_uri}")'}
#         # # Remove font-based properties to avoid conflicts
#         # updates["color"] = None
#         # updates["font-size"] = None

#         qss = merge_qss_properties(qss, css_selector, updates)

#     return qss
