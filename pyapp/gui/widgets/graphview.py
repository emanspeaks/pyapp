from ...logging import log_func_call
from ..qt import QGraphicsView, QGraphicsScene
from . import QtWidgetWrapper, GuiWidgetParentType


class GraphViewWidget(QtWidgetWrapper[QGraphicsView]):
    @log_func_call
    def __init__(self, parent: GuiWidgetParentType,
                 scene: QGraphicsScene = None):
        super().__init__(parent, scene)

    def create_qtobj(self, scene: QGraphicsScene = None):
        qtwin = self.gui_parent.gui_view.qtobj

        scene = scene or QGraphicsScene(qtwin)
        self.scene = scene

        view = QGraphicsView(scene, qtwin)
        self.view = view
        return view
