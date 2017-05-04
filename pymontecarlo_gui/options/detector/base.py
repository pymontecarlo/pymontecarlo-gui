""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo_gui.widgets.field import WidgetField

# Globals and constants variables.

class DetectorField(WidgetField):

    def isValid(self):
        return super().isValid() and bool(self.detectors())

    @abc.abstractmethod
    def detectors(self):
        """
        Returns a :class:`list` of :class:`Detector`.
        """
        return []
