""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.

# Globals and constants variables.

class ExecutionThread(QtCore.QThread):

    def __init__(self, function, parent=None):
        super().__init__(parent)
        self.function = function
        self.result = None

    def run(self):
        self.result = self.function()

class ExecutionProgressDialog(QtWidgets.QDialog):

    def __init__(self, title, running_message, success_message, function, timeout=1, parent=None):
        super().__init__(parent, QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
        self.setWindowTitle(title)

        # Variables
        self.success_message = success_message

        self.thread = ExecutionThread(function)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(timeout * 1000)
        self.timer.setSingleShot(True)

        self._function_result = None

        # Widgets
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setValue(0)

        self.label = QtWidgets.QLabel()
        self.label.setText(running_message)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.progress)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Signals
        self.thread.finished.connect(self._on_finished)
        self.timer.timeout.connect(self.accept)

    def _on_finished(self):
        self._function_result = self.thread.result
        self.label.setText(self.success_message)
        self.timer.start()

    def exec_(self):
        self.thread.start()
        super().exec_()

    def functionResult(self):
        return self._function_result