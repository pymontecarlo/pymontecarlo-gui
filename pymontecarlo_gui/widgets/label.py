""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.

# Globals and constants variables.

class LabelIcon(QtWidgets.QWidget):

    def __init__(self, text, icon, parent=None):
        super().__init__(parent)

        # Widgets
        self.lbl_text = QtWidgets.QLabel(text)

        self.lbl_icon = QtWidgets.QLabel()
        self.setIcon(icon)

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lbl_icon, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self.lbl_text, 1, QtCore.Qt.AlignLeft)
        layout.addStretch()
        self.setLayout(layout)

    def text(self):
        return self.lbl_text.text()

    def setText(self, text):
        self.lbl_text.setText(text)

    def setIcon(self, icon):
        self.lbl_icon.setPixmap(icon.pixmap(QtCore.QSize(16, 16)))
