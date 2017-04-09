""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.
from qtpy import QtWidgets, QtCore, QtGui

# Local modules.
from pymontecarlo.options.limit.showers import ShowersLimit

from pymontecarlo_gui.util.validate import Validable
from pymontecarlo_gui.widgets.label import LabelIcon
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.options.limit.showers import ShowersField

# Globals and constants variables.

class ProgramLimitsWidget(QtWidgets.QWidget, Validable):

    changed = QtCore.Signal()

    def __init__(self, widget_classes, parent=None):
        super().__init__(parent)

        # Widgets
        self.chk_auto = QtWidgets.QCheckBox('Auto')
        self.chk_auto.setChecked(True)

        self._widgets = []
        for clasz in widget_classes:
            widget = clasz()
            widget.setEnabled(False)
            self._widgets.append(widget)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.chk_auto)

        for widget in self._widgets:
            title = widget.accessibleName()
            lbl_description = QtWidgets.QLabel(widget.accessibleDescription())
            font = lbl_description.font()
            font.setItalic(True)
            lbl_description.setFont(font)
            lbl_description.setWordWrap(True)
            layout.addWidget(create_group_box(title, lbl_description, widget))

        layout.addStretch()
        self.setLayout(layout)

        # Signals
        self.chk_auto.stateChanged.connect(self._on_auto)

        for widget in self._widgets:
            widget.changed.connect(self.changed)

    def _on_auto(self):
        is_auto = self.chk_auto.isChecked()
        for widget in self._widgets:
            widget.setEnabled(not is_auto)
        self.changed.emit()

    def isValid(self):
        if self.chk_auto.isChecked():
            return super().isValid()
        return super().isValid() and \
            all(widget.isValid() for widget in self._widgets)

    def limits(self):
        if self.chk_auto.isChecked():
            return []

        limits = []

        for widget in self._widgets:
            limits.extend(widget.limits())

        return limits

class ProgramLimitsToolBox(QtWidgets.QWidget, Validable):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self.limit_widget_classes = {}
        self.limit_widget_classes[ShowersLimit] = ShowersWidget

        self._program_indexes = {}

        # Widgets
        self.toolbox = QtWidgets.QToolBox()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbox)
        self.setLayout(layout)

    def isValid(self):
        return super().isValid() and \
            all(self.toolbox.widget(index).isValid()
                for index in self._program_indexes.values())

    def addProgram(self, program):
        if program in self._program_indexes:
            return

        validator = program.create_validator()
        limit_classes = validator.limit_validate_methods.keys()
        widget_classes = [self.limit_widget_classes[clasz] for clasz in limit_classes]

        widget = ProgramLimitsWidget(widget_classes)
        widget.changed.connect(self.changed)

        name = program.create_configurator().fullname
        index = self.toolbox.addItem(widget, name)
        self._program_indexes[program] = index

    def removeProgram(self, program):
        if program not in self._program_indexes:
            return

        index = self._program_indexes.pop(program)
        self.toolbox.removeItem(index)

    def programs(self):
        return tuple(self._program_indexes.keys())

    def setPrograms(self, programs):
        for program in list(self._program_indexes):
            if program not in programs:
                self.removeProgram(program)

        for program in programs:
            self.addProgram(program)

    def limits(self):
        limits = {}

        for program, index in self._program_indexes.items():
            limits[program] = self.toolbox.widget(index).limits()

        return limits

class ProgramWidget(QtWidgets.QWidget, Validable):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._program = None
        self._errors = set()

        # Widgets
        self.checkbox = QtWidgets.QCheckBox()

        self.lbl_errors = LabelIcon()
        self.lbl_errors.setWordWrap(True)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox, QtCore.Qt.AlignLeft)
        layout.addWidget(self.lbl_errors, QtCore.Qt.AlignLeft)
        layout.addStretch()
        self.setLayout(layout)

        # Signals
        self.checkbox.stateChanged.connect(self.changed)

    def _errors_to_html(self, errors):
        html = '<ul>'

        errors = sorted(set(str(error) for error in errors))
        for error in errors:
            html += '<li>{}</li>'.format(error)

        html += '</ul>'

        return html

    def program(self):
        return self._program

    def setProgram(self, program):
        self._program = program
        self.checkbox.setText(program.create_configurator().fullname)

    def errors(self):
        return self._errors

    def setErrors(self, errors):
        self._errors = errors
        self.checkbox.setEnabled(not errors)

        text = self._errors_to_html(errors)
        self.lbl_errors.setText(text)

        icon = QtGui.QIcon.fromTheme('dialog-error') if errors else QtGui.QIcon()
        self.lbl_errors.setIcon(icon)

        self.adjustSize()

    def isValid(self):
        return super().isValid() and \
            self._program is not None and \
            not self._errors

    def isSelected(self):
        return self.isEnabled() and self.checkbox.isChecked()

    def setSelection(self, selected):
        self.checkbox.setChecked(selected)

class ProgramsWidget(QtWidgets.QWidget, Validable):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._widgets = OrderedDict()

        # Widgets
        self.scrollarea = QtWidgets.QScrollArea()
        self.scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollarea.setLineWidth(0)
        self.scrollarea.setFrameStyle(QtWidgets.QFrame.Plain)
        self.scrollarea.setWidgetResizable(True)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollarea)
        self.setLayout(layout)

    def isValid(self):
        selection = [widget for widget in self._widgets.values() if widget.isSelected()]
        if not selection:
            return False

        for widget in selection:
            if not widget.isValid():
                return False

        return super().isValid()

    def addProgram(self, program):
        program_widget = ProgramWidget()
        program_widget.setProgram(program)
        self._widgets[program] = program_widget

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for widget in self._widgets.values():
            layout.addWidget(widget)
        layout.addStretch()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.scrollarea.setWidget(widget)

        # Signals
        program_widget.changed.connect(self.changed)

    def setProgramErrors(self, program, errors):
        self._widgets[program].setErrors(errors)

    def selectedPrograms(self):
        return set(widget.program() for widget in self._widgets.values() if widget.isSelected())

    def programs(self):
        return set(widget.program() for widget in self._widgets.values())
