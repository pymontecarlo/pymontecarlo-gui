""""""

# Standard library modules.
import itertools

# Third party modules.
from qtpy import QtGui

# Local modules.

from pymontecarlo_gui.widgets.label import LabelIcon
from pymontecarlo_gui.widgets.field import CheckField, WidgetField, ToolBoxField

# Globals and constants variables.

class AutoField(CheckField):

    def title(self):
        return 'Auto'

class ProgramLimitsField(WidgetField):

    def __init__(self, program, limit_fields):
        self._program = program
        super().__init__()

        # Fields
        self.field_auto = AutoField()
        self.field_auto.setChecked(True)
        self.addCheckField(self.field_auto)

        self.limit_fields = limit_fields
        for field in limit_fields:
            field.setEnabled(False)
            self.addGroupField(field)

        # Signals
        self.field_auto.fieldChanged.connect(self._on_auto)

    def _on_auto(self):
        is_auto = self.field_auto.isChecked()
        for field in self.limit_fields:
            field.setEnabled(not is_auto)
        self.fieldChanged.emit()

    def title(self):
        return self.program().create_configurator().fullname

    def program(self):
        return self._program

    def isValid(self):
        if self.field_auto.isChecked():
            return True
        return super().isValid()

    def limits(self):
        if self.field_auto.isChecked():
            return []

        it = (field.limits() for field in self.limit_fields)
        return list(itertools.chain.from_iterable(it))

class LimitsToolBoxField(ToolBoxField):

    def __init__(self):
        super().__init__()

        self._limit_class_field = {}
        self._program_fields = {}

    def title(self):
        return 'Limit(s)'

    def registerLimitFieldClass(self, option_class, field_class):
        self._limit_class_field[option_class] = field_class

    def addProgram(self, program):
        if program in self._program_fields:
            return

        validator = program.create_validator()
        limit_classes = validator.limit_validate_methods.keys()

        limit_fields = []
        for clasz in limit_classes:
            if clasz not in self._limit_class_field:
                continue
            field = self._limit_class_field[clasz]()
            limit_fields.append(field)

        field = ProgramLimitsField(program, limit_fields)
        self._program_fields[program] = field
        self.addField(field)

    def removeProgram(self, program):
        if program not in self._program_fields:
            return

        field = self._program_fields.pop(program)
        self.removeField(field)

    def programs(self):
        return tuple(self._program_fields.keys())

    def setPrograms(self, programs):
        for program in self.programs():
            if program not in programs:
                self.removeProgram(program)

        for program in programs:
            self.addProgram(program)

    def limits(self):
        return dict((program, field.limits())
                    for program, field in self._program_fields.items())

class ProgramField(CheckField):

    def __init__(self, program):
        self._program = program
        self._errors = set()
        super().__init__()

        self._widget = LabelIcon()
        self._widget.setWordWrap(True)

    def _errors_to_html(self, errors):
        html = '<ul>'

        errors = sorted(set(str(error) for error in errors))
        for error in errors:
            html += '<li>{}</li>'.format(error)

        html += '</ul>'

        return html

    def title(self):
        return self.program().create_configurator().fullname

    def widget(self):
        return self._widget

    def program(self):
        return self._program

    def errors(self):
        return self._errors

    def setErrors(self, errors):
        self._errors = errors
        self.titleWidget().setEnabled(not errors)

        text = self._errors_to_html(errors)
        self._widget.setText(text)

        icon = QtGui.QIcon.fromTheme('dialog-error') if errors else QtGui.QIcon()
        self._widget.setIcon(icon)

    def hasErrors(self):
        return bool(self.errors())

    def isValid(self):
        return super().isValid() and not self.hasErrors()

class ProgramsField(WidgetField):

    def __init__(self):
        super().__init__()

        self._program_fields = {}

    def title(self):
        return 'Program(s)'

    def isValid(self):
        selection = [field for field in self.fields() if field.isChecked()]
        if not selection:
            return False

        for field in selection:
            if not field.isValid():
                return False

        return True

    def addProgram(self, program):
        field = ProgramField(program)
        self._program_fields[program] = field
        self.addCheckField(field)

    def setProgramErrors(self, program, errors):
        self._program_fields[program].setErrors(errors)

    def selectedPrograms(self):
        return set(field.program() for field in self.fields() if field.isChecked())

    def programs(self):
        return set(field.program() for field in self.fields())
