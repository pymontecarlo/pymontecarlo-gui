""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.photon import PhotonAnalysisFieldBase

from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysisBuilder

# Globals and constants variables.

class PhotonIntensityAnalysisField(PhotonAnalysisFieldBase):

    def title(self):
        return 'Photon intensity'

    def description(self):
        return 'Simulates X-rays and records their generated and emitted intensities'

    def analyses(self):
        builder = PhotonIntensityAnalysisBuilder()

        for detector in self.analysesToolBoxField().photonDetectors():
            builder.add_photon_detector(detector)

        return super().analyses() + builder.build()
