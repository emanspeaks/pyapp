from ....app import PyApp
from ...abc import QtDialogController, QtWindowController
from .view import ConfigTreeView


class ConfigTreeDialog(QtDialogController):
    def __init__(self, parent: QtWindowController):
        super().__init__(parent)
        self.window: ConfigTreeView = ConfigTreeView(self)

    def get_config(self):
        return PyApp.get_global_config()
