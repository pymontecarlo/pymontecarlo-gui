""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.

# Globals and constants variables.

class LabelIcon(QtWidgets.QWidget):

    def __init__(self, text='', icon=None, parent=None):
        super().__init__(parent)

        # Widgets
        self.lbl_icon = QtWidgets.QLabel()
        if icon:
            self.setIcon(icon)

        self.lbl_text = QtWidgets.QLabel(text)

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lbl_icon, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        layout.addWidget(self.lbl_text, 1)
        self.setLayout(layout)

    def text(self):
        return self.lbl_text.text()

    def setText(self, text):
        self.lbl_text.setText(text)

    def setIcon(self, icon):
        self.lbl_icon.setPixmap(icon.pixmap(QtCore.QSize(16, 16)))

    def setVerticalAlignment(self, alignment):
        layout = self.layout()
        layout.itemAt(0).setAlignment(alignment | QtCore.Qt.AlignHCenter)
        layout.itemAt(1).setAlignment(alignment | QtCore.Qt.AlignLeft)

    def wordWrap(self):
        return self.lbl_text.wordWrap()

    def setWordWrap(self, wrap):
        self.lbl_text.setWordWrap(wrap)
