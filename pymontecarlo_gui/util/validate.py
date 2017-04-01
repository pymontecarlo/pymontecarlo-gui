""""""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta

# Globals and constants variables.

INVALID_COLOR = 'pink'

VALID_BACKGROUND_STYLESHEET = 'background: none'
INVALID_BACKGROUND_STYLESHEET = 'background: ' + INVALID_COLOR

class Validable(metaclass=QABCMeta):

    @abc.abstractmethod
    def isValid(self):
        return True
