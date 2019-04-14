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

class AnalysisFieldBase(CheckFieldBase):

    def __init__(self):
        super().__init__()

        self._definition_field = None

    @abc.abstractmethod
    def definitionFieldClass(self):
        raise NotImplementedError

    def definitionField(self):
        if self._definition_field is None:
            self._definition_field = self.definitionFieldClass()()
        return self._definition_field

    def setDefinitionField(self, field):
        self._definition_field = field

    @abc.abstractmethod
    def analyses(self):
        return []

class AnalysesField(WidgetFieldBase):

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
        self.addCheckField(field)

    def selectedAnalysisFields(self):
        return set(field for field in self.fields() if field.isChecked())

    def selectedAnalyses(self):
        it = (field.analyses() for field in self.fields() if field.isChecked())
        return list(itertools.chain.from_iterable(it))
