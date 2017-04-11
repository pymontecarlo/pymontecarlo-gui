""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore

# Local modules.

# Globals and constants variables.

class FutureThread(QtCore.QThread):

    progressChanged = QtCore.Signal(int)

    def __init__(self, future):
        super().__init__()
        self.future = future

    def run(self):
        while self.future.running():
            self.progressChanged.emit(int(self.future.progress * 100))

        self.progressChanged.emit(100)

