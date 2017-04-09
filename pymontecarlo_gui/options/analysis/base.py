""""""

# Standard library modules.
import abc
import itertools

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
from pymontecarlo_gui.widgets.field import FieldToolBox, CheckField, WidgetField
from pymontecarlo_gui.options.detector.photon import PhotonDetectorField

# Globals and constants variables.

class AnalysesToolBoxMixin:

    def analysesToolBox(self):
        if not hasattr(self, '_toolbox'):
            self._toolbox = None
        return self._toolbox

    def setAnalysesToolBox(self, toolbox):
        self._toolbox = toolbox

class AnalysesToolBox(FieldToolBox):

    fieldChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._registered_requirements = {}

        # Fields
        self.field_photon_detector = PhotonDetectorField()

        # Signals
        self.field_photon_detector.fieldChanged.connect(self.fieldChanged)

    def _registerRequirement(self, analysis, field):
        if not self._registered_requirements.get(field, None):
            self.addField(field)

        self._registered_requirements.setdefault(field, set()).add(analysis)

    def _unregisterRequirement(self, analysis, field):
        if field not in self._registered_requirements:
            return

        self._registered_requirements[field].remove(analysis)

        if not self._registered_requirements[field]:
            self.removeField(field)

    def registerPhotonDetectorRequirement(self, analysis):
        self._registerRequirement(analysis, self.field_photon_detector)

    def unregisterPhotonDetectorRequirement(self, analysis):
        self._unregisterRequirement(analysis, self.field_photon_detector)

    def photonDetectors(self):
        return self.field_photon_detector.detectors()

class AnalysisField(CheckField, AnalysesToolBoxMixin):

    def __init__(self):
        super().__init__()

        self._widget = QtWidgets.QWidget()

        self.fieldChanged.connect(self._on_field_changed)

    def _on_field_changed(self):
        toolbox = self.analysesToolBox()

        if toolbox is not None:
            if self.isChecked():
                self._register_requirements(toolbox)
            else:
                self._unregister_requirements(toolbox)

    def _register_requirements(self, toolbox):
        pass

    def _unregister_requirements(self, toolbox):
        pass

    def widget(self):
        return CheckField.widget(self)

    @abc.abstractmethod
    def analyses(self):
        return []

class AnalysesField(WidgetField, AnalysesToolBoxMixin):

    def title(self):
        return 'Analyses'

    def isValid(self):
        selection = [field for field in self.fields() if field.isChecked()]
        if not selection:
            return False

        for field in selection:
            if not field.isValid():
                return False

        return True

    def addAnalysisField(self, field):
        field.setAnalysesToolBox(self.analysesToolBox())
        self.addCheckField(field)

    def setAnalysesToolBox(self, toolbox):
        super().setAnalysesToolBox(toolbox)
        for field in self.fields():
            field.setAnalysesToolBox(toolbox)

    def selectedAnalyses(self):
        return list(itertools.chain.from_iterable(field.analyses()
                                    for field in self.fields()
                                    if field.isChecked()))
