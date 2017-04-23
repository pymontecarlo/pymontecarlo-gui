""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta

# Globals and constants variables.

class ListToolBar(QtWidgets.QWidget, metaclass=QABCMeta):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._listwidget = None

        # Actions
        self.action_selectall = QtWidgets.QAction('Select all')
        self.action_selectall.setEnabled(False)

        self.action_unselectall = QtWidgets.QAction('Unselect all')
        self.action_unselectall.setEnabled(False)

        # Widgets
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.toolbar.addAction(self.action_selectall)
        self.toolbar.addAction(self.action_unselectall)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)

        # Signals
        self.action_selectall.triggered.connect(self._on_selectall)
        self.action_unselectall.triggered.connect(self._on_unselectall)

    def _on_list_changed(self):
        self._update_toolbar()

    def _on_selectall(self):
        for index in range(self.listWidget().count()):
            item = self.listWidget().item(index)
            self._select_item(item)

        self._update_toolbar()

    def _on_unselectall(self):
        for index in range(self.listWidget().count()):
            item = self.listWidget().item(index)
            self._unselect_item(item)

        self._update_toolbar()

    def _update_toolbar(self):
        if self.listWidget() is None:
            self.action_selectall.setEnabled(False)
            self.action_unselectall.setEnabled(False)
            return

        rows = self.listWidget().count()
        has_rows = rows > 0
        checked = sum(self._is_item_selected(self.listWidget().item(index))
                      for index in range(self.listWidget().count()))

        self.action_selectall.setEnabled(has_rows and checked < rows)
        self.action_unselectall.setEnabled(has_rows and checked > 0)

    @abc.abstractmethod
    def _select_item(self, item):
        raise NotImplementedError

    @abc.abstractmethod
    def _unselect_item(self, item):
        raise NotImplementedError

    @abc.abstractmethod
    def _is_item_selected(self, item):
        raise NotImplementedError

    def listWidget(self):
        return self._listwidget

    def setListWidget(self, widget):
        if self._listwidget is not None:
            self._listwidget.itemChanged.disconnect(self._on_list_changed)
            self._listwidget.itemSelectionChanged.disconnect(self._on_list_changed)
            self._listwidget.model().rowsInserted.disconnect(self._on_list_changed)

        widget.itemChanged.connect(self._on_list_changed)
        widget.model().rowsInserted.connect(self._on_list_changed)
        widget.itemSelectionChanged.connect(self._on_list_changed)

        self._listwidget = widget
        self._update_toolbar()

class CheckListToolBar(ListToolBar):

    def _select_item(self, item):
        item.setCheckState(QtCore.Qt.Checked)

    def _unselect_item(self, item):
        item.setCheckState(QtCore.Qt.Unchecked)

    def _is_item_selected(self, item):
        return item.checkState() == QtCore.Qt.Checked

class SelectionListToolBar(ListToolBar):

    def _select_item(self, item):
        item.setSelected(True)

    def _unselect_item(self, item):
        item.setSelected(False)

    def _is_item_selected(self, item):
        return item.isSelected()