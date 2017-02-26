""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.

class ColoredLineEdit(QtWidgets.QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Signals
        self.textChanged.connect(self._on_text_changed)

        # Defaults
        self._on_text_changed(self.text())

    def _on_text_changed(self, text):
        if self.hasAcceptableInput() or \
                not self.isEnabled():
            self.setStyleSheet("background: none")
        else:
            self.setStyleSheet("background: pink")

