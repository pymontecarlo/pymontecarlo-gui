""""""

# Standard library modules.

# Third party modules.
from qtpy import QtGui

# Local modules.
from pymontecarlo_gui.widgets.field import Field, WidgetField
from pymontecarlo_gui.widgets.icon import load_icon
from pymontecarlo_gui.results.summary import ResultSummaryTableWidget

# Globals and constants variables.

class _ProjectDerivedField(Field):

    def __init__(self, project):
        super().__init__()
        self._project = project

    def project(self):
        return self._project

    def setProject(self, project):
        self._project = project

class ProjectField(_ProjectDerivedField):

    def title(self):
        return 'Project'

    def icon(self):
        return QtGui.QIcon.fromTheme('user-home')

    def widget(self):
        return super().widget()

class ProjectSummaryTableField(_ProjectDerivedField):

    def __init__(self, project):
        super().__init__(project)
        self._widget = ResultSummaryTableWidget()
        self._widget.setProject(self.project())

    def title(self):
        return 'Summary table'

    def icon(self):
        return load_icon('table.svg')

    def widget(self):
        return self._widget

    def setProject(self, project):
        super().setProject(project)
        self._widget.setProject(project)

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

    def __init__(self, options):
        super().__init__()
        self._options = options

    def title(self):
        return 'Options'

    def icon(self):
        return QtGui.QIcon.fromTheme('document-properties')

    def options(self):
        return self._options

class ResultsField(Field):

    def title(self):
        return 'Results'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

