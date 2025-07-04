from PySide2.QtWidgets import QLabel, QFrame, QGraphicsView
from PySide2.QtCore import Qt

from ...logging import log_func_call
from ..abc import QtWindowBaseWidgetWrapper, QtWindowWrapper
from .graphview import GraphViewWidget


class WindowBaseLabel(QtWindowBaseWidgetWrapper):
    @log_func_call
    def __init__(self, parent: QtWindowWrapper, text: str = ""):
        super().__init__(parent)
        qtroot = QLabel(text, self.get_window_qtroot())
        self.qtroot: QLabel = qtroot
        qtroot.setAlignment(Qt.AlignCenter)


class WindowBaseGraphView(QtWindowBaseWidgetWrapper, GraphViewWidget):
    @log_func_call
    def __init__(self, parent: QtWindowWrapper):
        QtWindowBaseWidgetWrapper.__init__(self, parent)
        GraphViewWidget.__init__(self, parent)
        self.qtroot: QGraphicsView


class WindowBaseFrame(QtWindowBaseWidgetWrapper):
    @log_func_call
    def __init__(self, parent: QtWindowWrapper):
        super().__init__(parent)
        qtroot = QFrame(self.get_window_qtroot())
        self.qtroot: QFrame = qtroot
