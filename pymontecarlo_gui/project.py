""""""

# Standard library modules.

# Third party modules.
from qtpy import QtGui

# Local modules.
from pymontecarlo_gui.widgets.field import Field, WidgetField

# Globals and constants variables.

class ProjectField(Field):

    def title(self):
        return 'Project'

    def icon(self):
        return QtGui.QIcon.fromTheme('user-home')

    def widget(self):
        return super().widget()

class SimulationsField(Field):

    def title(self):
        return 'Simulations'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

class SimulationField(Field):

    def title(self):
        return 'Simulation'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

class OptionsField(WidgetField):

    def __init__(self):
        super().__init__()

        self._options = None

    def title(self):
        return 'Options'

    def icon(self):
        return QtGui.QIcon.fromTheme('document-properties')

    def options(self):
        return self._options

    def setOptions(self, options):
        self._options = options

class ResultsField(Field):

    def title(self):
        return 'Results'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

