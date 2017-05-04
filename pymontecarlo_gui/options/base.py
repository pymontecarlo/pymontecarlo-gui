""""""

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.util.tolerance import tolerance_to_decimals

from pymontecarlo_gui.widgets.field import MultiValueField
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit

# Globals and constants variables.

class DiameterField(MultiValueField):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        self._widget.setValues([100.0])

        # Widgets
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Diameter(s) [nm]'

    def widget(self):
        return self._widget

    def toleranceMeter(self):
        return self._widget.bottom()

    def setToleranceMeter(self, tolerance_m):
        decimals = tolerance_to_decimals(tolerance_m * 1e9)
        self._widget.setRange(tolerance_m, float('inf'), decimals)

    def diametersMeter(self):
        return np.array(self._widget.values()) * 1e-9

    def setDiametersMeter(self, diameters_m):
        values = np.array(diameters_m) * 1e9
        self._widget.setValues(values)