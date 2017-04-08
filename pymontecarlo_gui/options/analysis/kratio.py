""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.photon import PhotonAnalysisWidget

from pymontecarlo.options.analysis.kratio import KRatioAnalysisBuilder

# Globals and constants variables.

class KRatioAnalysisWidget(PhotonAnalysisWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName('k-ratio')
        self.setAccessibleDescription('Calculates k-ratios from X-ray intensities emitted from "unknown" and reference materials')

    def analyses(self):
        builder = KRatioAnalysisBuilder()

        for detector in self.analysisToolBox().photonDetectors():
            builder.add_photon_detector(detector)

        return super().analyses() + builder.build()
