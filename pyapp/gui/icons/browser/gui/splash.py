from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt

from pyapp.gui.abc import QtSplashScreen

from ..app import IconBrowserApp


class SplashScreen(QtSplashScreen):
    def __init__(self):
        splash_path = IconBrowserApp.get_assets_dir()/'SMPTE_Color_Bars.png'
        pm = QPixmap(splash_path.as_posix())
        super().__init__(pm.scaled(pm.width() * 2,
                                   pm.height() * 2,
                                   Qt.KeepAspectRatio,
                                   Qt.SmoothTransformation))
        self.set_progress(message="Loading IconBrowser...")
