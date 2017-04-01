""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtCore

# Local modules.

# Globals and constants variables.

class QABCMeta(type(QtCore.QObject), abc.ABCMeta):
    pass