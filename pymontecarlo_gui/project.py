""""""

# Standard library modules.

# Third party modules.
from qtpy import QtGui

# Local modules.
import pymontecarlo

from pymontecarlo_gui.widgets.field import Field
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
        self._widget = None

    def title(self):
        return 'Summary table'

    def icon(self):
        return load_icon('table.svg')

    def _create_widget(self):
        widget = ResultSummaryTableWidget()
        widget.setProject(self.project())

        pymontecarlo.settings.preferred_units_changed.connect(widget.update)
        pymontecarlo.settings.preferred_xrayline_notation_changed.connect(widget.update)
        pymontecarlo.settings.preferred_xrayline_encoding_changed.connect(widget.update)

        return widget

    def widget(self):
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def setProject(self, project):
        if self._widget is not None:
            self._widget.setProject(project)
        super().setProject(project)

class SimulationsField(Field):

    def title(self):
        return 'Simulations'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

class SimulationField(Field):

    def __init__(self, index, simulation):
        self._index = index
        self._simulation = simulation
        super().__init__()

    def title(self):
        return 'Simulation #{:d}'.format(self.index())

    def description(self):
        return self.simulation().identifier

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

    def index(self):
        return self._index

    def simulation(self):
        return self._simulation

class ResultsField(Field):

    def title(self):
        return 'Results'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

