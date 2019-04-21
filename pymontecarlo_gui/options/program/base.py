""""""

# Standard library modules.
import abc
import tempfile

# Third party modules.
from qtpy import QtGui
from unsync import unsync

# Local modules.
from pymontecarlo.util.error import ErrorAccumulator

from pymontecarlo_gui.widgets.field import WidgetFieldBase, CheckFieldBase
from pymontecarlo_gui.widgets.label import LabelIcon

# Globals and constants variables.

class ProgramFieldBase(WidgetFieldBase):

    _subclasses = []

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclasses.append(cls)

    def __init__(self, model, default_program):
        """
        Base class for all programs.

        :arg default_program: instance of the program
        """
        super().__init__()

        self.model = model
        self._default_program = default_program

    def isValid(self):
        return super().isValid() and bool(self.programs())

    @abc.abstractmethod
    def programs(self):
        """
        Returns a :class:`list` of :class:`Program`.
        """
        return []

    @unsync
    async def validateOptions(self, options, erracc):
        """
        Returns a :class:`set` of :class:`Exception` and
        a :class:`set` of :class:`Warning`.
        """
        oldprogram = options.program

        try:
            if not isinstance(options.program, self._default_program.__class__):
                options.program = self._default_program

            exporter = options.program.exporter

            with tempfile.TemporaryDirectory() as dirpath:
                await exporter._export(options, dirpath, erracc, dry_run=True)

        finally:
            options.program = oldprogram

        return erracc

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

        text = self._errors_to_html(errors)
        self._widget.setText(text)

        icon = QtGui.QIcon.fromTheme('dialog-error') if errors else QtGui.QIcon()
        self._widget.setIcon(icon)

    def isValid(self):
        return super().isValid() and not bool(self.errors())

class ProgramsField(WidgetFieldBase):

    def __init__(self):
        super().__init__()

    def title(self):
        return 'Program(s)'

    def isValid(self):
        # Selected fields
        selection = set(field for field in self.fields() if field.isChecked())
        if not selection:
            return False

        # Check field and program field must be valid
        for field in selection:
            if not field.isValid():
                return False
            if not field.programField().isValid():
                return False

        return True

    def addProgramField(self, program_field):
        field = CheckProgramField(program_field)
        self.addCheckField(field)

    def selectedProgramFields(self):
        return set(field.programField() for field in self.fields() if field.isChecked())

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
            erracc = ErrorAccumulator()

            for options in list_options:
                program_field.validateOptions(options, erracc).result()

            field.setErrors(erracc.exceptions)
