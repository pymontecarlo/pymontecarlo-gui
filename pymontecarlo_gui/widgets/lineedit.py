""""""

# Standard library modules.
import re
import math
import abc

# Third party modules.
from qtpy import QtWidgets, QtGui, QtCore

import numpy as np

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.util.validate import \
    Validable, VALID_BACKGROUND_STYLESHEET, INVALID_BACKGROUND_STYLESHEET

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

    def setRange(self, bottom, top, decimals=0):
        self._get_double_validator().setRange(bottom, top, decimals)

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

class ColoredLineEdit(QtWidgets.QLineEdit, Validable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Signals
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        if not self.isEnabled():
            self.setStyleSheet(VALID_BACKGROUND_STYLESHEET)
            return

        if self.hasAcceptableInput():
            self.setStyleSheet(VALID_BACKGROUND_STYLESHEET)
        else:
            self.setStyleSheet(INVALID_BACKGROUND_STYLESHEET)

    def isValid(self):
        return super().isValid() and self.hasAcceptableInput()

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self._on_text_changed(self.text())

    def setValidator(self, validator):
        super().setValidator(validator)
        self._on_text_changed(self.text())

class ColoredFloatLineEdit(QtWidgets.QWidget,
                           LineEditAdapterMixin,
                           DoubleValidatorAdapterMixin,
                           Validable):

    valueChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.lineedit = ColoredLineEdit()
        self.lineedit.setValidator(QtGui.QDoubleValidator())
        self._update_tooltip()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)

        # Signals
        self.lineedit.textChanged.connect(self._on_text_changed)
        self.lineedit.validator().changed.connect(self._on_validator_changed)

    def _update_tooltip(self):
        locale = QtCore.QLocale.system()
        precision = self.decimals()
        tooltip = 'Value must be between [{}, {}]' \
            .format(locale.toString(self.bottom(), 'f', precision),
                    locale.toString(self.top(), 'f', precision))
        self.lineedit.setToolTip(tooltip)
        self.setToolTip(tooltip)

    def _on_text_changed(self, *args):
        self.valueChanged.emit(self.value())

    def _on_validator_changed(self, *args):
        self._update_tooltip()
        self.setValue(self.value())

    def _get_double_validator(self):
        return self.lineedit.validator()

    def _get_lineedit(self):
        return self.lineedit

    def isValid(self):
        if not super().isValid():
            return False

        if not self.lineedit.isValid():
            return False

        locale = QtCore.QLocale.system()
        _value, ok = locale.toDouble(self.lineedit.text())
        if not ok:
            return False

        return True

    def value(self):
        locale = QtCore.QLocale.system()
        value, ok = locale.toDouble(self.lineedit.text())
        if not ok:
            return float('nan')
        else:
            return value

    def setValue(self, value):
        locale = QtCore.QLocale.system()
        precision = self.decimals()
        if precision == 0:
            if not math.isfinite(value):
                value = 0
            value = int(value)
            text = locale.toString(value)
        else:
            value = float(value)
            text = locale.toString(value, 'f', precision)
        self.lineedit.setText(text)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.lineedit.setEnabled(enabled)

MULTIFLOAT_SEPARATOR = ';'
MULTIFLOAT_PATTERN = r'(?P<start>inf|[\de\.+\-\,]*)(?:\:(?P<stop>[\de\.+\-\,]*))?(?:\:(?P<step>[\de\.+\-\,]*))?'

def parse_multifloat_text(text):
    locale = QtCore.QLocale.system()

    values = []

    for part in text.split(MULTIFLOAT_SEPARATOR):
        part = part.strip()
        if not part:
            continue

        match = re.match(MULTIFLOAT_PATTERN, part)
        if not match:
            raise ValueError('Invalid part: %s' % part)

        start, _ok = locale.toDouble(match.group('start'))

        stop = match.group('stop')
        if stop is None:
            stop = start + 1
        else:
            stop, _ok = locale.toDouble(stop)

        step = match.group('step')
        if step is None:
            step = 1
        else:
            step, _ok = locale.toDouble(step)

        if math.isinf(start):
            values.append(start)
        else:
            values.extend(np.arange(start, stop, step))

    return tuple(sorted(set(values)))

class MultiFloatValidator(QtGui.QValidator, DoubleValidatorAdapterMixin):

    def __init__(self):
        super().__init__()

        # Variables
        expr = QtCore.QRegExp(r'^[\de\-.,+:;]+$')
        self.validator_text = QtGui.QRegExpValidator(expr)
        self.validator_value = QtGui.QDoubleValidator()

        # Signals
        self.validator_text.changed.connect(self.changed)
        self.validator_value.changed.connect(self.changed)

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
            if self.decimals() == 0:
                text = str(int(value))
            else:
                locale = QtCore.QLocale.system()
                text = locale.toString(value, 'g', self.decimals())
            state, _, _ = self.validator_value.validate(text, pos)
            if state != QtGui.QValidator.Acceptable:
                return state, input, pos

        return QtGui.QValidator.Acceptable, input, pos

    def _get_double_validator(self):
        return self.validator_value

class ColoredMultiFloatLineEdit(QtWidgets.QWidget,
                                LineEditAdapterMixin,
                                DoubleValidatorAdapterMixin,
                                Validable):

    valuesChanged = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.lineedit = ColoredLineEdit()
        self.lineedit.setValidator(MultiFloatValidator())
        self._update_tooltip()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)

        # Signals
        self.lineedit.textChanged.connect(self._on_text_changed)
        self.lineedit.validator().changed.connect(self._on_validator_changed)

    def _update_tooltip(self):
        locale = QtCore.QLocale.system()
        precision = self.decimals()
        tooltip = 'Value(s) must be between [{}, {}]' \
            .format(locale.toString(self.bottom(), 'f', precision),
                    locale.toString(self.top(), 'f', precision))
        self.lineedit.setToolTip(tooltip)
        self.setToolTip(tooltip)

    def _on_text_changed(self, *args):
        self.valuesChanged.emit(self.values())

    def _on_validator_changed(self, *args):
        self._update_tooltip()
        self.setValues(self.values())

    def _get_double_validator(self):
        return self.lineedit.validator()

    def _get_lineedit(self):
        return self.lineedit

    def isValid(self):
        if not super().isValid():
            return False

        if not self.lineedit.isValid():
            return False

        try:
            parse_multifloat_text(self.lineedit.text())
        except:
            return False

        return True

    def values(self):
        try:
            return parse_multifloat_text(self.lineedit.text())
        except:
            return ()

    def setValues(self, values):
        locale = QtCore.QLocale.system()
        precision = self.decimals()

        text_values = []
        for value in values:
            if precision == 0:
                value = int(value)
                text_values.append(locale.toString(value))
            else:
                value = float(value)
                text_values.append(locale.toString(value, 'f', precision))

        text = MULTIFLOAT_SEPARATOR.join(text_values)
        self.lineedit.setText(text)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.lineedit.setEnabled(enabled)

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
