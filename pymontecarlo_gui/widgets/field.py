""""""

# Standard library modules.
import abc
import functools

# Third party modules.
from qtpy import QtWidgets, QtCore, QtGui

# Local modules.
from pymontecarlo_gui.util.validate import Validable
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.widgets.groupbox import create_group_box

# Globals and constants variables.

class Field(QtCore.QObject, Validable, metaclass=QABCMeta):

    changed = QtCore.Signal()

    @abc.abstractmethod
    def label(self):
        return QtWidgets.QLabel()

    @abc.abstractmethod
    def widget(self):
        return QtWidgets.QWidget()

    def suffix(self):
        return None

    def isValid(self):
        if not super().isValid():
            return False

        widget = self.widget()
        if isinstance(widget, Validable) and not widget.isValid():
            return False

        return True

class FieldLayout(QtWidgets.QGridLayout):

    def addLabelField(self, field):
        row = self.rowCount()
        suffix = field.suffix()
        has_suffix = suffix is not None

        # Label
        self.addWidget(field.label(), row, 0)

        # Widget
        colspan = 1 if has_suffix else 2
        self.addWidget(field.widget(), row, 1, 1, colspan)

        # Suffix
        if has_suffix:
            self.addWidget(suffix, row, 2)

    def addGroupField(self, field):
        row = self.rowCount()

        suffix = field.suffix()
        if suffix is not None:
            widgets = [field.widget(), suffix]
        else:
            widgets = [field.widget()]

        groupbox = create_group_box(field.label().text(), *widgets)
        self.addWidget(groupbox, row, 0, 1, 3)

class FieldToolBox(QtWidgets.QToolBox, Validable):

    def _on_field_changed(self, index, field):
        if field.isValid():
            icon = QtGui.QIcon()
        else:
            icon = QtGui.QIcon.fromTheme("dialog-error")

        self.setItemIcon(index, icon)

    def isValid(self):
        for index in range(self.count()):
            widget = self.widget(index)
            if not isinstance(widget, Validable):
                continue
            if not widget.isValid():
                return False

        return super().isValid()

    def addLabelFields(self, title, *fields):
        lyt_fields = FieldLayout()
        lyt_fields.setContentsMargins(0, 0, 0, 0)
        for field in fields:
            lyt_fields.addLabelField(field)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(lyt_fields)
        layout.addStretch()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        index = self.addItem(widget, title)

        for field in fields:
            field.changed.connect(functools.partial(self._on_field_changed, index, field))

        return index

    def addGroupField(self, field):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(field.widget())
        layout.addStretch()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        title = field.label().text()
        index = self.addItem(widget, title)

        field.changed.connect(functools.partial(self._on_field_changed, index, field))

        return index

