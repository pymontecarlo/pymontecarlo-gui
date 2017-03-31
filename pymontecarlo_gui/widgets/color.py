""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

import matplotlib.colors

# Local modules.

# Globals and constants variables.

def check_color(color):
    try:
        color = QtGui.QColor(color)
    except:
        r, g, b, a = matplotlib.colors.to_rgba(color)
        color = QtGui.QColor()
        color.setRgbF(r, g, b, a)
    return color

class ColorButton(QtWidgets.QPushButton):

    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._color = QtCore.Qt.white
        self._padding = 5

    def color(self):
        return self._color

    def rgba(self):
        return (self._color.redF(), self._color.greenF(), self._color.blueF(), self._color.alphaF())

    def setColor(self, color):
        color = check_color(color)
        self._color = color
        self.colorChanged.emit(color)

    def padding(self):
        return self._padding

    def setPadding(self, pad):
        self._padding = int(pad)

    def paintEvent(self, event):
        super().paintEvent(event)

        color = self.color()
        padding = self.padding()

        rect = event.rect()
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtCore.Qt.NoPen)
        rect.adjust(padding, padding, -1 - padding, -1 - padding)
        painter.drawRect(rect)
        painter.end()

class ColorDialogButton(QtWidgets.QWidget):

    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.button = ColorButton()
        self.button.setFixedSize(QtCore.QSize(25, 25))
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Signals
        self.button.clicked.connect(self._on_clicked)
        self.button.colorChanged.connect(self.colorChanged)

    def _on_clicked(self):
        dialog = QtWidgets.QColorDialog(self.color())

        if not dialog.exec_():
            return

        self.setColor(dialog.selectedColor())
        self.button.repaint()

    def color(self):
        return self.button.color()

    def rgba(self):
        return self.button.rgba()

    def setColor(self, color):
        self.button.setColor(color)

def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = ColorDialogButton()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__':
    run()

