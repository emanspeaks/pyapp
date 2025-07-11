from typing import TYPE_CHECKING

from PySide2.QtWidgets import (
    QToolBar, QComboBox, QListView, QLineEdit, QVBoxLayout,
    QShortcut,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence

from pyapp.gui.abc import QtWindowWrapper, get_gui_app
from pyapp.gui.widgets.windowbase import WindowBaseFrame
from pyapp.gui.loadstatus import load_status_step
from pyapp.gui.utils import (
    create_action, create_toolbar_expanding_spacer,
    set_widget_sizepolicy_expanding, show_toolbtn_icon_and_text
)

from ...app import IconBrowserApp
from ...logging import log_func_call
from ..gui_icons import ConfigIcon, CopyCodeIcon, CopyNameIcon
from ..constants import (
    ALL_COLLECTIONS, DEFAULT_VIEW_COLUMNS, VIEW_COLUMNS_OPTIONS
)
from .iconlistview import IconListView
if TYPE_CHECKING:
    from .ctrl import MainWindow


class MainWindowView(QtWindowWrapper):
    @log_func_call
    def __init__(self, controller: 'MainWindow'):
        super().__init__(IconBrowserApp.APP_NAME, controller)
        self.basewidget: WindowBaseFrame
        self.controller: MainWindow
        self.get_window_qtroot().resize(*IconBrowserApp.get_default_win_size())
        qtroot = self.qtroot
        qtroot.setMinimumSize(900, 600)

        layout = QVBoxLayout()
        self.layout = layout
        self.get_qtbasewidget().setLayout(layout)

        self.create_toolbars()
        self.create_icon_list_view()
        self.set_tab_order()
        self.setup_shortcuts()

        self.lineEditFilter.setFocus()
        self.center_window_in_current_screen()
        self.controller.updateStyle(self.comboStyle.currentText())

    @load_status_step("Creating toolbars")
    @log_func_call
    def create_toolbars(self):
        self.create_filter_toolbar()
        self.create_name_toolbar()
        # self.create_view_toolbar()

    @log_func_call
    def create_filter_toolbar(self):
        qtroot = self.qtroot
        ctrl = self.controller

        toolbar = QToolBar("Filters", qtroot)
        qtroot.addToolBar(Qt.TopToolBarArea, toolbar)
        qtroot.addToolBarBreak()
        self.filter_toolbar = toolbar

        comboFont = QComboBox()
        comboFont.setToolTip(
            "Select the font prefix whose icons will be included in "
            "the filtering."
        )
        comboFont.setMaximumWidth(125)
        comboFont.addItems([ALL_COLLECTIONS]
                           + sorted(ctrl.get_font_names()))
        comboFont.currentIndexChanged.connect(ctrl.triggerImmediateUpdate)
        comboFont = comboFont
        self.comboFont = comboFont
        toolbar.addWidget(comboFont)

        lineEditFilter = QLineEdit()
        lineEditFilter.setToolTip("Filter icons by name")
        lineEditFilter.setMinimumWidth(200)
        # lineEditFilter.setMaximumWidth(400)
        set_widget_sizepolicy_expanding(lineEditFilter)
        lineEditFilter.setAlignment(Qt.AlignLeft)
        lineEditFilter.textChanged.connect(ctrl.filter_text_changed)
        lineEditFilter.returnPressed.connect(ctrl.triggerImmediateUpdate)  # noqa: E501
        lineEditFilter.setClearButtonEnabled(True)
        lineEditFilter.setPlaceholderText("Search icons")
        self.lineEditFilter = lineEditFilter
        toolbar.addWidget(lineEditFilter)

    @log_func_call
    def create_name_toolbar(self):
        qtroot = self.qtroot
        ctrl = self.controller

        toolbar = QToolBar("Icon Name", qtroot)
        qtroot.addToolBar(Qt.TopToolBarArea, toolbar)
        self.name_toolbar = toolbar

        # Icon name section
        nameField = QLineEdit()
        nameField.setPlaceholderText(
            "(Full identifier of the currently selected icon)"
        )
        nameField.setAlignment(Qt.AlignCenter)
        nameField.setReadOnly(True)
        nameField.setFixedWidth(400)
        fnt = nameField.font()
        fnt.setFamily("monospace")
        fnt.setBold(True)
        nameField.setFont(fnt)
        self.nameField = nameField
        toolbar.addWidget(nameField)

        toolbar.addSeparator()

        copyButton = create_action(qtroot, "Copy Name", CopyNameIcon.icon(),
                                   ctrl.copyIconText, enabled=False,
                                   tooltip="Copy selected icon "
                                   "full identifier to the clipboard")
        self.copyButton = copyButton
        toolbar.addAction(copyButton)
        show_toolbtn_icon_and_text(toolbar.widgetForAction(copyButton))

        copyPyAppButton = create_action(qtroot, "Copy PyApp Code",
                                        CopyCodeIcon.icon(),
                                        ctrl.copyIconPyAppCode, enabled=False,
                                        tooltip="Copy selected icon "
                                        "PyApp code to the clipboard")
        self.copyPyAppButton = copyPyAppButton
        toolbar.addAction(copyPyAppButton)
        show_toolbtn_icon_and_text(toolbar.widgetForAction(copyPyAppButton))

        # @log_func_call
        # def create_view_toolbar(self):
        # qtroot = self.qtroot
        # ctrl = self.controller
        app = get_gui_app()

        # toolbar = QToolBar("View", qtroot)
        # qtroot.addToolBar(Qt.TopToolBarArea, toolbar)
        # self.view_toolbar = toolbar

        toolbar.addWidget(create_toolbar_expanding_spacer())

        # Display (columns number) section
        comboColumns = QComboBox()
        comboColumns.setToolTip(
            "Select number of columns the icons list is showing"
        )
        for num_columns in VIEW_COLUMNS_OPTIONS:
            comboColumns.addItem(str(num_columns), num_columns)
        comboColumns.setCurrentIndex(
            comboColumns.findData(DEFAULT_VIEW_COLUMNS)
        )
        comboColumns.currentTextChanged.connect(ctrl.updateColumns)
        comboColumns.setMinimumWidth(75)
        self.comboColumns = comboColumns
        toolbar.addWidget(comboColumns)

        # Style section
        comboStyle = QComboBox()
        comboStyle.setToolTip(
            "Select color palette for the icons and the icon browser"
        )
        current_theme = app.get_theme()
        theme_idx = None
        themes = app.themes.list_themes(always_include_qdarkstyle=True)
        for i, t in enumerate(sorted(themes)):
            comboStyle.addItem(t, i)
            if t == current_theme:
                theme_idx = i

        comboStyle.setCurrentIndex(theme_idx if theme_idx is not None else 0)
        comboStyle.currentTextChanged.connect(ctrl.updateStyle)
        comboStyle.setMinimumWidth(100)
        self.comboStyle = comboStyle
        toolbar.addWidget(comboStyle)

        toolbar.addAction(create_action(qtroot, "Config", ConfigIcon.icon(),
                                        ctrl.click_config))

    @log_func_call
    def create_basewidget(self):
        return WindowBaseFrame(self)

    @log_func_call
    def create_icon_list_view(self):
        ctrl = self.controller
        listview = IconListView(DEFAULT_VIEW_COLUMNS, self)
        self.listView = listview

        lvwidget = listview.qtroot
        lvwidget.setUniformItemSizes(True)
        lvwidget.setViewMode(QListView.IconMode)
        lvwidget.setModel(ctrl.proxyModel)
        lvwidget.setContextMenuPolicy(Qt.CustomContextMenu)
        lvwidget.doubleClicked.connect(ctrl.doubleClickIcon)
        selmodel = lvwidget.selectionModel()
        selmodel.selectionChanged.connect(ctrl.updateNameField)
        self.layout.addWidget(lvwidget)

    @log_func_call
    def set_tab_order(self):
        qtroot = self.qtroot
        qtroot.setTabOrder(self.comboFont, self.lineEditFilter)
        qtroot.setTabOrder(self.lineEditFilter, self.comboColumns)
        qtroot.setTabOrder(self.comboColumns, self.comboStyle)
        qtroot.setTabOrder(self.comboStyle, self.listView.qtroot)
        qtroot.setTabOrder(self.listView.qtroot, self.nameField)
        qtroot.setTabOrder(self.nameField, self.comboFont)

    @log_func_call
    def setup_shortcuts(self):
        # Shortcuts
        ctrl = self.controller
        qtroot = self.qtroot
        QShortcut(QKeySequence(Qt.Key_Return), qtroot, ctrl.copyIconText)
        QShortcut(QKeySequence("Ctrl+F"), qtroot, self.lineEditFilter.setFocus)
