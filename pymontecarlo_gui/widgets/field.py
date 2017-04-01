""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtWidgets, QtCore

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta

# Globals and constants variables.

class Field(QtCore.QObject, metaclass=QABCMeta):

    @abc.abstractmethod
    def label(self):
        return QtWidgets.QLabel('')

    @abc.abstractmethod
    def widget(self):
        return QtWidgets.QWidget()

    def suffix(self):
        return None

    def addToGridLayout(self, layout, row, start_column=0):
        layout.addWidget(self.label(), row, start_column)
        layout.addWidget(self.widget(), row, start_column + 1)

        suffix = self.suffix()
        if suffix is not None:
            layout.addWidget(suffix, row, start_column + 2)

