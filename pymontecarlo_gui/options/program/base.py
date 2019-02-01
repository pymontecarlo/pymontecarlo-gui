""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtGui

# Local modules.
from pymontecarlo_gui.widgets.field import WidgetFieldBase, CheckFieldBase
from pymontecarlo_gui.widgets.label import LabelIcon

# Globals and constants variables.

class ProgramFieldBase(WidgetFieldBase):

    def __init__(self, default_program):
        """
        Base class for all programs.
        
        :arg default_program: instance of the program
        """
        super().__init__()

        self._default_program = default_program

    def isValid(self):
        return super().isValid() and bool(self.programs())

    @abc.abstractmethod
    def programs(self):
        """
        Returns a :class:`list` of :class:`Program`.
        """
        return []

    def validateOptions(self, options):
        """
        Returns a :class:`set` of :class:`Exception` and 
        a :class:`set` of :class:`Warning`.
        """
        errors = set()
        warnings = set()
#        options.program = self._default_program
#        self._validator._validate_options(options, errors, warnings)

        return errors, warnings

class CheckProgramField(CheckFieldBase):

    def __init__(self, program_field):
        self._program_field = program_field
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
        return self.programField().title()

    def widget(self):
        return self._widget

    def programField(self):
        return self._program_field

    def errors(self):
        return self._errors

    def setErrors(self, errors):
        self._errors = errors
        self.titleWidget().setEnabled(not errors)

        if errors:
            self.setChecked(False)

        text = self._errors_to_html(errors)
        self._widget.setText(text)

        icon = QtGui.QIcon.fromTheme('dialog-error') if errors else QtGui.QIcon()
        self._widget.setIcon(icon)

    def hasErrors(self):
        return bool(self.errors())

    def isValid(self):
        return super().isValid() and not self.hasErrors()

class ProgramsField(WidgetFieldBase):

    def __init__(self):
        super().__init__()

    def title(self):
        return 'Program(s)'

    def isValid(self):
        selection = self.selectedProgramFields()
        if not selection:
            return False

        for field in selection:
            if not field.isValid():
                return False

        return True

    def addProgramField(self, program_field):
        field = CheckProgramField(program_field)
        self.addCheckField(field)

    def selectedProgramFields(self):
        return set(field.programField() for field in self.fields()
                   if field.isChecked() and not field.hasErrors())

    def programFields(self):
        return set(field.programField() for field in self.fields())

    def programs(self):
        programs = []
        for field in self.selectedProgramFields():
            programs.extend(field.programs())
        return programs

    def updateErrors(self, list_options):
        for field in self.fields():
            program_field = field.programField()
            errors = set()

            for options in list_options:
                field_errors, _field_warnings = program_field.validateOptions(options)
                errors |= field_errors

            field.setErrors(errors)

