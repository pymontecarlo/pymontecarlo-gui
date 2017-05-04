""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo_gui.widgets.field import WidgetField

# Globals and constants variables.

class LimitField(WidgetField):

    def isValid(self):
        return super().isValid() and bool(self.limits())

    @abc.abstractmethod
    def limits(self):
        """
        Returns a :class:`list` of :class:`Limits`.
        """
        return []
