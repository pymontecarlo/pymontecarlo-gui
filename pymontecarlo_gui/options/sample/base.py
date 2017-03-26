""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.

class SampleWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def samples(self):
        """
        Returns a :class:`list` of :class:`Sample`.
        """
        return []

    def setAvailableMaterials(self, materials):
        raise NotImplementedError

    def availableMaterials(self):
        raise NotImplementedError
