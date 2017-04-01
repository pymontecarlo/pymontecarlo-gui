""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtWidgets, QtCore

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.widgets.groupbox import create_group_box

# Globals and constants variables.

class Field(QtCore.QObject, metaclass=QABCMeta):

    @abc.abstractmethod
    def widget(self):
        return QtWidgets.QWidget()

    @abc.abstractmethod
    def addToGridLayout(self, layout, row, start_column=0):
        raise NotImplementedError

class LabelField(Field):

    @abc.abstractmethod
    def label(self):
        return QtWidgets.QLabel('')

    def suffix(self):
        return None

    def addToGridLayout(self, layout, row, start_column=0):
        suffix = self.suffix()
        has_suffix = suffix is not None

        # Label
        layout.addWidget(self.label(), row, start_column)

        # Widget
        colspan = 1 if has_suffix else 2
        layout.addWidget(self.widget(), row, start_column + 1, 1, colspan)

        # Suffix
        if has_suffix:
            layout.addWidget(suffix, row, start_column + 2)

class GroupField(Field):

    def _create_group_box(self):
        return create_group_box(self.title(), self.widget())

    @abc.abstractmethod
    def title(self):
        return ''

    def addToGridLayout(self, layout, row, start_column=0):
        groupbox = self._create_group_box()
        layout.addWidget(groupbox, row, start_column, 1, 3)
