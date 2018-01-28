""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta

# Globals and constants variables.

class ResultSummaryWidgetBase(QtWidgets.QWidget, metaclass=QABCMeta):

    @abc.abstractmethod
    def setProject(self, project):
        raise NotImplementedError
