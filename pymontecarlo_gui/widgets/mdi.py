""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.

# Globals and constants variables.


class MdiSubWindow(QtWidgets.QMdiSubWindow):

    closed = QtCore.Signal()

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
