from typing import TYPE_CHECKING

from PySide2.QtWidgets import (
    QToolBar, QComboBox, QListView, QLineEdit, QPushButton, QVBoxLayout,
    QShortcut,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence, QCursor

from pyapp.gui.abc import QtWindowWrapper, get_qt_app
from pyapp.gui.widgets.windowbase import WindowBaseFrame
from pyapp.gui.loadstatus import load_status_step
from pyapp.gui.utils import create_action, create_toolbar_expanding_spacer
from pyapp.gui.themes import DEFAULT_DARK_PALETTE, DEFAULT_LIGHT_PALETTE

from ...app import IconBrowserApp
from ...logging import log_func_call
from ..icons import ConfigIcon
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
        self.set_window_geometry()
        self.controller.updateStyle(self.comboStyle.currentText())

    @load_status_step("Creating toolbars")
    def create_toolbars(self):
        self.create_filter_toolbar()
        self.create_name_toolbar()
        self.create_view_toolbar()

    def create_filter_toolbar(self):
        qtroot = self.qtroot
        ctrl = self.controller

        toolbar = QToolBar("Filters", qtroot)
        qtroot.addToolBar(Qt.TopToolBarArea, toolbar)
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
        lineEditFilter.setMaximumWidth(400)
        lineEditFilter.setToolTip("Filter icons by name")
        lineEditFilter.setAlignment(Qt.AlignLeft)
        lineEditFilter.textChanged.connect(ctrl.triggerDelayedUpdate)
        lineEditFilter.returnPressed.connect(ctrl.triggerImmediateUpdate)  # noqa: E501
        lineEditFilter.setClearButtonEnabled(True)
        self.lineEditFilter = lineEditFilter
        toolbar.addWidget(lineEditFilter)

    def create_name_toolbar(self):
        qtroot = self.qtroot
        ctrl = self.controller

        toolbar = QToolBar("Icon Name", qtroot)
        qtroot.addToolBar(Qt.TopToolBarArea, toolbar)
        self.name_toolbar = toolbar

        # Icon name section
        nameField = QLineEdit()
        nameField.setPlaceholderText(
            "Full identifier of the currently selected icon"
        )
        nameField.setAlignment(Qt.AlignCenter)
        nameField.setReadOnly(True)
        nameField.setFixedWidth(300)
        fnt = nameField.font()
        fnt.setFamily("monospace")
        fnt.setBold(True)
        nameField.setFont(fnt)
        self.nameField = nameField
        toolbar.addWidget(nameField)

        toolbar.addSeparator()

        copyButton = QPushButton("Copy Name")
        copyButton.setToolTip(
            "Copy selected icon full identifier to the clipboard"
        )
        copyButton.clicked.connect(ctrl.copyIconText)
        copyButton.setDisabled(True)
        self.copyButton = copyButton
        toolbar.addWidget(copyButton)

        copyPyAppButton = QPushButton("Copy PyApp Code")
        copyPyAppButton.setToolTip(
            "Copy selected icon PyApp code to the clipboard"
        )
        copyPyAppButton.clicked.connect(ctrl.copyIconPyAppCode)
        copyPyAppButton.setDisabled(True)
        self.copyPyAppButton = copyPyAppButton
        toolbar.addWidget(copyPyAppButton)

    def create_view_toolbar(self):
        qtroot = self.qtroot
        ctrl = self.controller

        toolbar = QToolBar("View", qtroot)
        qtroot.addToolBar(Qt.TopToolBarArea, toolbar)
        self.view_toolbar = toolbar

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
        comboStyle.addItem(DEFAULT_DARK_PALETTE, 0)
        comboStyle.addItem(DEFAULT_LIGHT_PALETTE, 1)
        comboStyle.currentTextChanged.connect(ctrl.updateStyle)
        comboStyle.setMinimumWidth(100)
        self.comboStyle = comboStyle
        toolbar.addWidget(comboStyle)

        toolbar.addWidget(create_toolbar_expanding_spacer())
        toolbar.addAction(create_action(qtroot, "Config", ConfigIcon.icon(),
                                        ctrl.click_config))

    @log_func_call
    def create_basewidget(self):
        return WindowBaseFrame(self)

    def create_icon_list_view(self):
        ctrl = self.controller
        listview = IconListView(DEFAULT_VIEW_COLUMNS, self)
        self.listView = listview

        lvwidget = listview.qtroot
        lvwidget.setUniformItemSizes(True)
        lvwidget.setViewMode(QListView.IconMode)
        lvwidget.setModel(ctrl.proxyModel)
        lvwidget.setContextMenuPolicy(Qt.CustomContextMenu)
        lvwidget.doubleClicked.connect(ctrl.copyIconText)
        selmodel = lvwidget.selectionModel()
        selmodel.selectionChanged.connect(ctrl.updateNameField)
        self.layout.addWidget(lvwidget)

    def set_tab_order(self):
        qtroot = self.qtroot
        qtroot.setTabOrder(self.comboFont, self.lineEditFilter)
        qtroot.setTabOrder(self.lineEditFilter, self.comboStyle)
        qtroot.setTabOrder(self.comboStyle, self.listView.qtroot)
        qtroot.setTabOrder(self.listView.qtroot, self.nameField)
        qtroot.setTabOrder(self.nameField, self.copyButton)
        qtroot.setTabOrder(self.copyButton, self.copyPyAppButton)
        qtroot.setTabOrder(self.copyPyAppButton, self.comboFont)

    def setup_shortcuts(self):
        # Shortcuts
        ctrl = self.controller
        qtroot = self.qtroot
        QShortcut(QKeySequence(Qt.Key_Return), qtroot, ctrl.copyIconText)
        QShortcut(QKeySequence("Ctrl+F"), qtroot, self.lineEditFilter.setFocus)

    def set_window_geometry(self):
        qtroot = self.qtroot
        qtapp = get_qt_app()
        centerPoint = qtapp.screenAt(QCursor.pos()).geometry().center()
        geo = qtroot.geometry()
        geo.moveCenter(centerPoint)
        qtroot.setGeometry(geo)
