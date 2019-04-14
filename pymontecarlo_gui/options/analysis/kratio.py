""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.photon import PhotonAnalysisFieldBase

from pymontecarlo.options.analysis.kratio import KRatioAnalysisBuilder

# Globals and constants variables.

class KRatioAnalysisField(PhotonAnalysisFieldBase):

    def title(self):
        return 'k-ratio'

    def description(self):
        return 'Calculates k-ratios from X-ray intensities emitted from "unknown" and reference materials'

    def analyses(self):
        builder = KRatioAnalysisBuilder()

        for detector in self.definitionField().detectors():
            builder.add_photon_detector(detector)

        return super().analyses() + builder.build()
