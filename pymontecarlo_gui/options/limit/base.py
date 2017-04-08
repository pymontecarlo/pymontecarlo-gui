""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtWidgets, QtCore

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.util.validate import Validable

# Globals and constants variables.

class LimitWidget(QtWidgets.QWidget, Validable, metaclass=QABCMeta):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def isValid(self):
        return super().isValid() and bool(self.limits())

    @abc.abstractmethod
    def limits(self):
        """
        Returns a :class:`list` of :class:`Limits`.
        """
        return []
