""""""

# Standard library modules.
import re
import math
import locale

# Third party modules.
from qtpy import QtWidgets, QtGui

import numpy as np

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

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self._on_text_changed(self.text())

class ColoredFloatLineEdit(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_lineedit = ColoredLineEdit()
        self.wdg_lineedit.setValidator(QtGui.QDoubleValidator())

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.wdg_lineedit)
        self.setLayout(layout)

        # Signals
        self.wdg_lineedit.textChanged.connect(self._on_text_changed)

        # Defaults
        self._on_text_changed(self.wdg_lineedit.text())

    def _on_text_changed(self, text):
        if self.wdg_lineedit.hasAcceptableInput() or \
                not self.isEnabled():
            self.setStyleSheet("background: none")
        else:
            self.setStyleSheet("background: pink")

    def clear(self):
        self.wdg_lineedit.clear()

    def value(self):
        try:
            return locale.atof(self.wdg_lineedit.text())
        except ValueError:
            return float('nan')

    def setValue(self, value):
        fmt = '%.{}f'.format(self.decimals())
        self.wdg_lineedit.setText(locale.format(fmt, value))

    def range(self):
        return self.wdg_lineedit.validator().range()

    def setRange(self, top, bottom):
        self.wdg_lineedit.validator().setRange(top, bottom)

    def decimals(self):
        return self.wdg_lineedit.validator().decimals()

    def setDecimals(self, decimals):
        self.wdg_lineedit.validator().setDecimals(decimals)

def parse_text(text):
    VALUE_SEPARATOR = ';'
    PATTERN = r'(?P<start>inf|[\de\.+\-]*)(?:\:(?P<stop>[\de\.+\-]*))?(?:\:(?P<step>[\de\.+\-]*))?'

    values = []

    for part in text.split(VALUE_SEPARATOR):
        part = part.strip()
        if not part:
            continue

        match = re.match(PATTERN, part)
        if not match:
            raise ValueError('Invalid part: %s' % part)

        start = float(match.group('start'))
        stop = float(match.group('stop') or start + 1)
        step = float(match.group('step') or 1)

        if math.isinf(start):
            values.append(start)
        else:
            values.extend(np.arange(start, stop, step))

    return np.array(values)

def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    widget = ColoredFloatLineEdit()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__':
    run()
