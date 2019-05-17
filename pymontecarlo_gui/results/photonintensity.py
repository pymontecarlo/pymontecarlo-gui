""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.results.base import ResultTableWidgetBase, ResultFieldBase
from pymontecarlo_gui.results.photon import PhotonSingleResultModel

# Globals and constants variables.

class PhotonIntensityResultWidget(ResultTableWidgetBase):

    def _create_model(self, result, settings):
        return PhotonSingleResultModel(result, settings, 'Intensity', '1/(sr.electron)')

class PhotonIntensityResultField(ResultFieldBase):

    def __init__(self, result, settings):
        super().__init__(result, settings)

        # Widgets
        self._widget = PhotonIntensityResultWidget(result, settings)

    def widget(self):
        return self._widget
