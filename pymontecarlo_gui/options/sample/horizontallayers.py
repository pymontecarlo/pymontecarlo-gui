""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSampleBuilder

from pymontecarlo_gui.options.sample.base import \
    AngleField, MaterialWidgetField, LayerBuilderField, SampleFieldBase

# Globals and constants variables.

class SubstrateField(MaterialWidgetField):

    def __init__(self):
        super().__init__()
        self.field_material._widget.setRequiresSelection(False)

    def title(self):
        return "Substrate (optional)"

class HorizontalLayerSampleField(SampleFieldBase):

    def __init__(self):
        super().__init__()

        self.field_layers = LayerBuilderField()
        self.addField(self.field_layers)

        self.field_substrate = SubstrateField()
        self.addField(self.field_substrate)

        self.field_angle = AngleField()
        self.addField(self.field_angle)

    def title(self):
        return 'Horizontal layered sample'

    def description(self):
        return 'A multi-layer sample'

    def setAvailableMaterials(self, materials):
        self.field_layers.setAvailableMaterials(materials)
        self.field_substrate.setAvailableMaterials(materials)

    def samples(self):
        builder = HorizontalLayerSampleBuilder()

        for layer_builder in self.field_layers.layerBuilders():
            builder.add_layer_builder(layer_builder)

        for material in self.field_substrate.materials():
            builder.add_substrate_material(material)

        for tilt_deg in self.field_angle.tiltsDegree():
            builder.add_tilt_deg(tilt_deg)

        for azimuth_deg in self.field_angle.azimuthsDegree():
            builder.add_azimuth_deg(azimuth_deg)

        return super().samples() + builder.build()

def run(): #pragma: no cover
    import sys

    app = QtWidgets.QApplication(sys.argv)

    field = HorizontalLayerSampleField()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(field.widget())
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
