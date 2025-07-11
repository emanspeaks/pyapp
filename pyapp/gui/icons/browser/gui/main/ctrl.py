from PySide2.QtCore import QTimer, QSortFilterProxyModel, Qt

from pyapp.gui.icons.iconfont.sources import THIRDPARTY_FONTSPEC
from pyapp.gui.abc import QtWindowController, get_qt_app, get_gui_app
from pyapp.gui.dialogs.config import ConfigTreeDialog

from ...logging import log_func_call, DEBUGLOW2
from ..constants import AUTO_SEARCH_TIMEOUT, ALL_COLLECTIONS
from ..utils import iconstring_to_specname_iconname

from .view import MainWindowView
from .iconmodel import IconModel


class MainWindow(QtWindowController):
    @log_func_call
    def __init__(self):
        # need models before creating the view
        self.create_filter_models()

        super().__init__()
        win = MainWindowView(self)
        self.window: MainWindowView = win
        # qtroot = win.qtroot

        self.create_timer()

    @log_func_call
    def create_filter_models(self):
        model = IconModel()
        model.setStringList(sorted(self.get_icon_names()))

        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(model)
        proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel = proxyModel

    @log_func_call
    def create_timer(self):
        filterTimer = QTimer(self.get_window_qtroot())
        filterTimer.setSingleShot(True)
        filterTimer.setInterval(AUTO_SEARCH_TIMEOUT)
        filterTimer.timeout.connect(self.updateFilter)
        self.filterTimer = filterTimer

    @log_func_call
    def click_config(self):
        dlg = ConfigTreeDialog(self)
        dlg.show()

    @log_func_call(DEBUGLOW2)
    def get_icon_names(self):
        iconNames = []
        for k, v in THIRDPARTY_FONTSPEC.items():
            iconNames += [f'{k}:{icon}' for icon in v.charmap.keys()]

        return iconNames

    @log_func_call(DEBUGLOW2, trace_only=True)
    def get_font_names(self):
        return THIRDPARTY_FONTSPEC.keys()

    @log_func_call(DEBUGLOW2, trace_only=True)
    def triggerImmediateUpdate(self):
        """
        Stop the timer used for committing the search term and update the
        proxy model immediately.
        """
        self.filterTimer.stop()
        self.updateFilter()

    @log_func_call(DEBUGLOW2, trace_only=True)
    def updateFilter(self):
        win = self.window
        reString = ""

        group = win.comboFont.currentText()
        if group != ALL_COLLECTIONS:
            reString += rf"^{group}:"

        searchTerm = win.lineEditFilter.text()
        if searchTerm:
            reString += rf".*{searchTerm}.*$"

        # QSortFilterProxyModel.setFilterRegExp has been removed in Qt 6.
        # Instead, QSortFilterProxyModel.setFilterRegularExpression is
        # supported in Qt 5.12 or later.
        self.proxyModel.setFilterRegularExpression(reString)

    @log_func_call
    def doubleClickIcon(self):
        self.updateNameField()
        self.copyIconPyAppCode()

    @log_func_call
    def copyIconText(self):
        """
        Copy the name of the currently selected icon to the clipboard.
        """
        indexes = self.window.listView.qtroot.selectedIndexes()
        if not indexes:
            return

        clipboard = get_qt_app().clipboard()
        clipboard.setText(indexes[0].data())

    @log_func_call
    def copyIconPyAppCode(self):
        indexes = self.window.listView.qtroot.selectedIndexes()
        if not indexes:
            return

        iconstring = indexes[0].data()
        specname, iconname = iconstring_to_specname_iconname(iconstring)
        spec = THIRDPARTY_FONTSPEC[specname]
        fontmod = spec.module_qualname()
        fontclass = spec.classname
        shortname = spec.shortname

        code = ("from pyapp.gui.icons.iconfont import IconSpec\n"
                f"from {fontmod} import {fontclass}\n"
                f"from {fontmod} import names as {shortname}_names  # noqa: E501\n"
                f"{shortname}_{iconname}_ispec = IconSpec.generate_iconspec({fontclass}, glyph={shortname}_names.{iconname})  # noqa: E501\n")

        clipboard = get_qt_app().clipboard()
        clipboard.setText(code)

    @log_func_call
    def updateNameField(self):
        """
        Update field to the name of the currently selected icon.
        """
        win = self.window
        indexes = win.listView.qtroot.selectedIndexes()
        if not indexes:
            win.nameField.setText("")
            win.copyButton.setDisabled(True)
            win.copyPyAppButton.setDisabled(True)
            return

        win.nameField.setText(indexes[0].data())
        win.copyButton.setDisabled(False)
        win.copyPyAppButton.setDisabled(False)

    @log_func_call(DEBUGLOW2, trace_only=True)
    def triggerDelayedUpdate(self):
        self.filterTimer.stop()
        self.filterTimer.start()

    @log_func_call(DEBUGLOW2, trace_only=True)
    def filter_text_changed(self):
        self.style_placeholder_text()
        self.triggerDelayedUpdate()

    @log_func_call
    def updateStyle(self, text: str):
        # qtawesome.reset_cache()
        get_gui_app().set_theme(text)

    @log_func_call
    def updateColumns(self):
        win = self.window
        win.listView.setColumns(win.comboColumns.currentData())

    @log_func_call(DEBUGLOW2, trace_only=True)
    def style_placeholder_text(self):
        win = self.window
        txtbox = win.lineEditFilter
        txtbox.style().polish(txtbox)
