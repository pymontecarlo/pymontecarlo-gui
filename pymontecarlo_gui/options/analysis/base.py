""""""

# Standard library modules.
import abc
import itertools

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo_gui.widgets.field import CheckFieldBase, WidgetFieldBase, ToolBoxFieldBase
from pymontecarlo_gui.options.detector.photon import PhotonDetectorField

# Globals and constants variables.

class AnalysesToolBoxMixin:

    def analysesToolBoxField(self):
        if not hasattr(self, '_field_toolbox'):
            self._field_toolbox = None
        return self._field_toolbox

    def setAnalysesToolBoxField(self, field):
        self._field_toolbox = field

class AnalysesToolBoxField(ToolBoxFieldBase):

    def __init__(self):
        super().__init__()

        self._registered_requirements = {}

        self.field_photon_detector = PhotonDetectorField()

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

    def title(self):
        return 'Definition'

    def registerPhotonDetectorRequirement(self, analysis):
        self._registerRequirement(analysis, self.field_photon_detector)

    def unregisterPhotonDetectorRequirement(self, analysis):
        self._unregisterRequirement(analysis, self.field_photon_detector)

    def photonDetectors(self):
        return self.field_photon_detector.detectors()

class AnalysisFieldBase(CheckFieldBase, AnalysesToolBoxMixin):

    def __init__(self):
        super().__init__()

        self._widget = QtWidgets.QWidget()

        self.fieldChanged.connect(self._on_field_changed)

    def _on_field_changed(self):
        field_toolbox = self.analysesToolBoxField()

        if field_toolbox is not None:
            if self.isChecked():
                self._register_requirements(field_toolbox)
            else:
                self._unregister_requirements(field_toolbox)

    def _register_requirements(self, field_toolbox):
        pass

    def _unregister_requirements(self, field_toolbox):
        pass

    @abc.abstractmethod
    def analyses(self):
        return []

class AnalysesField(WidgetFieldBase, AnalysesToolBoxMixin):

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
        field.setAnalysesToolBoxField(self.analysesToolBoxField())
        self.addCheckField(field)

    def setAnalysesToolBoxField(self, field):
        super().setAnalysesToolBoxField(field)
        for field in self.fields():
            field.setAnalysesToolBoxField(field)

    def selectedAnalyses(self):
        it = (field.analyses() for field in self.fields() if field.isChecked())
        return list(itertools.chain.from_iterable(it))
