from ....app import PyApp
from ....logging import log_func_call
from ...abc import QtDialogController, QtWindowController
from .view import ConfigTreeView


class ConfigTreeDialog(QtDialogController):
    @log_func_call
    def __init__(self, parent: QtWindowController):
        super().__init__(parent)
        self.window: ConfigTreeView = ConfigTreeView(self)

    @log_func_call
    def get_config(self):
        return PyApp.get_global_config()
