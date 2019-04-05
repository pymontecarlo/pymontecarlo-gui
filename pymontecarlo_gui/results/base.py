""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.

class ResultSummaryWidgetBase(QtWidgets.QWidget):

    def setProject(self, project):
        raise NotImplementedError
