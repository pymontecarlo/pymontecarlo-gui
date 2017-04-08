""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.photon import PhotonAnalysisWidget

from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysisBuilder

# Globals and constants variables.

class PhotonIntensityAnalysisWidget(PhotonAnalysisWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName('Photon intensity')
        self.setAccessibleDescription('Simulates X-rays and records their generated and emitted intensities')

    def analyses(self):
        if not self.checkbox.isChecked():
            return super().analyses()

        builder = PhotonIntensityAnalysisBuilder()

        for detector in self.analysisToolBox().photonDetectors():
            builder.add_photon_detector(detector)

        return super().analyses() + builder.build()
