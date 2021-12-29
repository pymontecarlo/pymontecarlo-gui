""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo_gui.widgets.field import WidgetFieldBase

# Globals and constants variables.


class DetectorFieldBase(WidgetFieldBase):
    def isValid(self):
        return super().isValid() and bool(self.detectors())

    @abc.abstractmethod
    def detectors(self):
        """
        Returns a :class:`list` of :class:`Detector`.
        """
        return []
