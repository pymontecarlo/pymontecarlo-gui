""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.results.base import ResultTableWidgetBase, ResultFieldBase
from pymontecarlo_gui.results.photon import PhotonSingleResultModel

# Globals and constants variables.

class KRatioResultWidget(ResultTableWidgetBase):

    def _create_model(self, result, settings):
        return PhotonSingleResultModel(result, settings, 'k-ratio')

class KRatioResultField(ResultFieldBase):

    def __init__(self, result, settings):
        super().__init__(result, settings)

        # Widgets
        self._widget = KRatioResultWidget(result, settings)

    def widget(self):
        return self._widget
