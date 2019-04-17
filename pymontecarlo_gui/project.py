""""""

# Standard library modules.
import os

# Third party modules.
from qtpy import QtCore, QtGui

# Local modules.
from pymontecarlo_gui.widgets.field import FieldBase
from pymontecarlo_gui.widgets.icon import load_icon
from pymontecarlo_gui.results.summary import \
    ResultSummaryTableWidget, ResultSummaryFigureWidget

# Globals and constants variables.

class _SettingsBasedField(FieldBase):

    settingsChanged = QtCore.Signal()

    def __init__(self, settings):
        self._settings = settings
        super().__init__()

    def settings(self):
        return self._settings

class _ProjectDerivedField(_SettingsBasedField):

    def __init__(self, settings, project):
        self._project = project
        super().__init__(settings)

    def project(self):
        return self._project

    def setProject(self, project):
        self._project = project

class ProjectField(_ProjectDerivedField):

    def title(self):
        if self.project().filepath is not None:
            return 'Project ({})'.format(os.path.basename(self.project().filepath))
        else:
            return 'Project'

    def icon(self):
        return QtGui.QIcon.fromTheme('user-home')

    def widget(self):
        return super().widget()

class ProjectSummaryTableField(_ProjectDerivedField):

    def __init__(self, settings, project):
        super().__init__(settings, project)
        self._widget = None

    def title(self):
        return 'Summary table'

    def icon(self):
        return load_icon('table.svg')

    def _create_widget(self):
        widget = ResultSummaryTableWidget(self.settings())
        widget.setProject(self.project())
        return widget

    def widget(self):
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def setProject(self, project):
        if self._widget is not None:
            self._widget.setProject(project)
        super().setProject(project)

class ProjectSummaryFigureField(_ProjectDerivedField):

    def __init__(self, settings, project):
        super().__init__(settings, project)
        self._widget = None

    def title(self):
        return 'Summary figure'

    def icon(self):
        return load_icon('figure.svg')

    def _create_widget(self):
        widget = ResultSummaryFigureWidget(self.settings())
        widget.setProject(self.project())
        return widget

    def widget(self):
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def setProject(self, project):
        if self._widget is not None:
            self._widget.setProject(project)
        super().setProject(project)

class SimulationsField(FieldBase):

    def title(self):
        return 'Simulations'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

class SimulationField(FieldBase):

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

class ResultsField(FieldBase):

    def title(self):
        return 'Results'

    def icon(self):
        return QtGui.QIcon.fromTheme('folder')

    def widget(self):
        return super().widget()

