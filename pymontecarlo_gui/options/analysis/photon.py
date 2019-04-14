""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.base import AnalysisFieldBase
from pymontecarlo_gui.options.detector.photon import PhotonDetectorField

# Globals and constants variables.

class PhotonAnalysisFieldBase(AnalysisFieldBase):

    def definitionFieldClass(self):
        return PhotonDetectorField
