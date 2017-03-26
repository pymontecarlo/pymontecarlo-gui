""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.

class BeamWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def beams(self):
        """
        Returns a :class:`list` of :class:`Beam`.
        """
        return []

class BeamPositionWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def positions(self):
        """
        Returns a :class:`list` of :class:`tuple` for the x and y positions.
        """
        return []
