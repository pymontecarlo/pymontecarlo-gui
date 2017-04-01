""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtWidgets, QtCore

# Local modules.
from pymontecarlo_gui.util.validate import Validable
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.widgets.groupbox import create_group_box

# Globals and constants variables.

class Field(QtCore.QObject, Validable, metaclass=QABCMeta):

    @abc.abstractmethod
    def _add_to_layout(self, layout, row):
        raise NotImplementedError

    @abc.abstractmethod
    def widget(self):
        return QtWidgets.QWidget()

    def isValid(self):
        if not super().isValid():
            return False

        widget = self.widget()
        if isinstance(widget, Validable) and not widget.isValid():
            return False

        return True

class LabelField(Field):

    def _add_to_layout(self, layout, row):
        suffix = self.suffix()
        has_suffix = suffix is not None

        # Label
        layout.addWidget(self.label(), row, 0)

        # Widget
        colspan = 1 if has_suffix else 2
        layout.addWidget(self.widget(), row, 1, 1, colspan)

        # Suffix
        if has_suffix:
            layout.addWidget(suffix, row, 2)

    @abc.abstractmethod
    def label(self):
        return QtWidgets.QLabel('')

    def suffix(self):
        return None

class GroupField(Field):

    def _create_group_box(self):
        return create_group_box(self.title(), self.widget())

    def _add_to_layout(self, layout, row):
        groupbox = self._create_group_box()
        layout.addWidget(groupbox, row, 0, 1, 3)

    @abc.abstractmethod
    def title(self):
        return ''

class FieldLayout(QtWidgets.QGridLayout):

    def addField(self, field):
        row = self.rowCount()
        field._add_to_layout(self, row)
