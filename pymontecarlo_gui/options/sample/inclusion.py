""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

import numpy as np

# Local modules.
from pymontecarlo.options.sample.inclusion import InclusionSample, InclusionSampleBuilder
from pymontecarlo.util.tolerance import tolerance_to_decimals

from pymontecarlo_gui.options.sample.base import \
    SampleField, AngleField, MaterialWidgetField
from pymontecarlo_gui.widgets.field import MultiValueField
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit

# Globals and constants variables.

class InclusionDiameterField(MultiValueField):

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

class SubstrateField(MaterialWidgetField):

    def title(self):
        return 'Substrate'

class InclusionField(MaterialWidgetField):

    def __init__(self):
        super().__init__()

        self.field_diameter = InclusionDiameterField()
        self.field_diameter.setToleranceMeter(InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)
        self.addLabelField(self.field_diameter)

    def title(self):
        return 'Inclusion'

    def diametersMeter(self):
        return self.field_diameter.diametersMeter()

    def setDiametersMeter(self, diameters_m):
        self.field_diameter.setDiametersMeter(diameters_m)

class InclusionSampleField(SampleField):

    def __init__(self):
        super().__init__()

        self.field_substrate = SubstrateField()
        self.addField(self.field_substrate)

        self.field_inclusion = InclusionField()
        self.addField(self.field_inclusion)

        self.field_angle = AngleField()
        self.addField(self.field_angle)

    def title(self):
        return 'Inclusion'

    def description(self):
        return 'An half-sphere inclusion in a substrate'

    def setAvailableMaterials(self, materials):
        self.field_substrate.setAvailableMaterials(materials)
        self.field_inclusion.setAvailableMaterials(materials)

    def samples(self):
        builder = InclusionSampleBuilder()

        for material in self.field_substrate.materials():
            builder.add_substrate_material(material)

        for material in self.field_inclusion.materials():
            builder.add_inclusion_material(material)

        for diameter_m in self.field_inclusion.diametersMeter():
            builder.add_inclusion_diameter_m(diameter_m)

        for tilt_deg in self.field_angle.tiltsDegree():
            builder.add_tilt_deg(tilt_deg)

        for azimuth_deg in self.field_angle.azimuthsDegree():
            builder.add_azimuth_deg(azimuth_deg)

        return super().samples() + builder.build()

def run(): #pragma: no cover
    import sys
    app = QtWidgets.QApplication(sys.argv)

    field = InclusionSampleField()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(field.widget())
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
