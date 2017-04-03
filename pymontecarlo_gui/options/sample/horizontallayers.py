""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSampleBuilder

from pymontecarlo_gui.options.sample.base import \
    TiltField, RotationField, MaterialField, LayerBuilderField, SampleWidget
from pymontecarlo_gui.widgets.field import FieldLayout

# Globals and constants variables.

class SubstrateMaterialField(MaterialField):

    def __init__(self):
        super().__init__()
        self._widget.setRequiresSelection(False)

    def title(self):
        return "Substrate material(s) (optional)"

class HorizontalLayerSampleWidget(SampleWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName('Horizontal layered sample')
        self.setAccessibleDescription('A multi-layer sample')

        # Widgets
        self.field_layers = LayerBuilderField()

        self.field_substrate = SubstrateMaterialField()

        self.field_tilt = TiltField()

        self.field_rotation = RotationField()

        # Layouts
        layout = FieldLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addField(self.field_layers)
        layout.addField(self.field_substrate)
        layout.addField(self.field_tilt)
        layout.addField(self.field_rotation)
        self.setLayout(layout)

        # Signals
        self.field_layers.layerBuildersChanged.connect(self.samplesChanged)
        self.field_substrate.materialsChanged.connect(self.samplesChanged)
        self.field_tilt.tiltsChanged.connect(self.samplesChanged)
        self.field_rotation.rotationsChanged.connect(self.samplesChanged)

    def isValid(self):
        return super().isValid() and \
            self.field_layers.isValid() and \
            self.field_substrate.isValid() and \
            self.field_tilt.isValid() and \
            self.field_rotation.isValid()

    def setAvailableMaterials(self, materials):
        self.field_layers.setAvailableMaterials(materials)
        self.field_substrate.setAvailableMaterials(materials)

    def samples(self):
        builder = HorizontalLayerSampleBuilder()

        for layer_builder in self.field_layers.layerBuilders():
            builder.add_layer_builder(layer_builder)

        for material in self.field_substrate.materials():
            builder.add_substrate_material(material)

        for tilt_deg in self.field_tilt.tilts_deg():
            builder.add_tilt_deg(tilt_deg)

        for rotation_deg in self.field_rotation.rotations_deg():
            builder.add_rotation_deg(rotation_deg)

        return super().samples() + builder.build()

def run(): #pragma: no cover
    import sys
    from qtpy import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    table = HorizontalLayerSampleWidget()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
