""""""

# Standard library modules.
import re
import math
import locale
import abc

# Third party modules.
from qtpy import QtWidgets, QtGui, QtCore

import numpy as np

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta

# Globals and constants variables.

class DoubleValidatorAdapterMixin(metaclass=QABCMeta):

    @abc.abstractmethod
    def _get_double_validator(self): #pragma: no cover
        raise NotImplementedError

    def bottom(self):
        return self._get_double_validator().bottom()

    def setBottom(self, bottom):
        self._get_double_validator().setBottom(bottom)

    def decimals(self):
        return self._get_double_validator().decimals()

    def setDecimals(self, decimals):
        self._get_double_validator().setDecimals(decimals)

    def range(self):
        return self._get_double_validator().range()

    def setRange(self, top, bottom, decimals=0):
        self._get_double_validator().setRange(top, bottom, decimals)

    def top(self):
        return self._get_double_validator().top()

    def setTop(self, top):
        self._get_double_validator().setTop(top)

class LineEditAdapterMixin(metaclass=QABCMeta):

    @abc.abstractmethod
    def _get_lineedit(self): #pragma: no cover
        raise NotImplementedError

    def keyPressEvent(self, event):
        self._get_lineedit().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self._get_lineedit().keyReleaseEvent(event)

    def clear(self):
        self._get_lineedit().clear()

    def hasAcceptableInput(self):
        return self._get_lineedit().hasAcceptableInput()

class ColoredLineEdit(QtWidgets.QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Signals
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        if self.hasAcceptableInput() or \
                not self.isEnabled():
            self.setStyleSheet("background: none")
        else:
            self.setStyleSheet("background: pink")

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self._on_text_changed(self.text())

    def setValidator(self, validator):
        super().setValidator(validator)
        self._on_text_changed(self.text())

class ColoredFloatLineEdit(QtWidgets.QWidget,
                           LineEditAdapterMixin,
                           DoubleValidatorAdapterMixin):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.lineedit = ColoredLineEdit()
        self.lineedit.setValidator(QtGui.QDoubleValidator())

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)

    def _get_double_validator(self):
        return self.lineedit.validator()

    def _get_lineedit(self):
        return self.lineedit

    def value(self):
        try:
            return locale.atof(self.lineedit.text())
        except ValueError:
            return float('nan')

    def setValue(self, value):
        fmt = '%.{}f'.format(self.decimals())
        text = locale.format(fmt, value)
        self.lineedit.setText(text)

MULTIFLOAT_SEPARATOR = ';'
MULTIFLOAT_PATTERN = r'(?P<start>inf|[\de\.+\-]*)(?:\:(?P<stop>[\de\.+\-]*))?(?:\:(?P<step>[\de\.+\-]*))?'

def parse_multifloat_text(text):
    values = []

    for part in text.split(MULTIFLOAT_SEPARATOR):
        part = part.strip()
        if not part:
            continue

        match = re.match(MULTIFLOAT_PATTERN, part)
        if not match:
            raise ValueError('Invalid part: %s' % part)

        start = locale.atof(match.group('start'))

        stop = match.group('stop')
        stop = locale.atof(stop) if stop is not None else start + 1

        step = match.group('step')
        step = locale.atof(step) if step is not None else 1

        if math.isinf(start):
            values.append(start)
        else:
            values.extend(np.arange(start, stop, step))

    return sorted(set(values))

class MultiFloatValidator(QtGui.QValidator, DoubleValidatorAdapterMixin):

    def __init__(self):
        super().__init__()

        expr = QtCore.QRegExp(r'^[\de\-.,+:;]+$')
        self.validator_text = QtGui.QRegExpValidator(expr)
        self.validator_value = QtGui.QDoubleValidator()

    def validate(self, input, pos):
        if not input:
            return QtGui.QValidator.Intermediate, input, pos

        state, input, pos = self.validator_text.validate(input, pos)
        if state == QtGui.QValidator.Invalid:
            return state, input, pos

        try:
            values = parse_multifloat_text(input)
        except:
            return QtGui.QValidator.Intermediate, input, pos

        for value in values:
            state, _, _ = self.validator_value.validate(str(value), pos)
            if state != QtGui.QValidator.Acceptable:
                return state, input, pos

        return QtGui.QValidator.Acceptable, input, pos

    def _get_double_validator(self):
        return self.validator_value

class ColoredMultiFloatLineEdit(QtWidgets.QWidget,
                                LineEditAdapterMixin,
                                DoubleValidatorAdapterMixin):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.lineedit = ColoredLineEdit()
        self.lineedit.setValidator(MultiFloatValidator())

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)

    def _get_double_validator(self):
        return self.lineedit.validator()

    def _get_lineedit(self):
        return self.lineedit

    def values(self):
        try:
            return parse_multifloat_text(self.lineedit.text())
        except:
            return ()

    def setValues(self, values):
        fmt = '%.{}f'.format(self.decimals())
        text = MULTIFLOAT_SEPARATOR.join(locale.format(fmt, v) for v in values)
        self.lineedit.setText(text)

def run(): #pragma: no cover
    import sys
    app = QtWidgets.QApplication(sys.argv)


    widget = ColoredMultiFloatLineEdit()
    widget.setRange(1.0, 5.0, 2)
    widget.setValues([3.0, 4.12345])

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
