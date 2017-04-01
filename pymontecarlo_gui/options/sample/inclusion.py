""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo.options.sample.inclusion import InclusionSample, InclusionSampleBuilder

from pymontecarlo_gui.widgets.field import FieldLayout
from pymontecarlo_gui.options.sample.base import \
    SampleWidget, TiltField, RotationField, MaterialField, DiameterField

# Globals and constants variables.

class SubstrateMaterialField(MaterialField):

    def title(self):
        return 'Substrate material(s)'

class InclusionMaterialField(MaterialField):

    def title(self):
        return 'Inclusion material(s)'

class InclusionDiameterField(DiameterField):

    def _get_tolerance_m(self):
        return InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m

class InclusionSampleWidget(SampleWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.field_substrate = SubstrateMaterialField()

        self.field_inclusion = InclusionMaterialField()

        self.field_diameter = InclusionDiameterField()

        self.field_tilt = TiltField()

        self.field_rotation = RotationField()

        # Layouts
        layout = FieldLayout()
        layout.addField(self.field_substrate)
        layout.addField(self.field_inclusion)
        layout.addField(self.field_diameter)
        layout.addField(self.field_tilt)
        layout.addField(self.field_rotation)
        self.setLayout(layout)

    def setAvailableMaterials(self, materials):
        self.field_substrate.setAvailableMaterials(materials)
        self.field_inclusion.setAvailableMaterials(materials)

    def samples(self):
        builder = InclusionSampleBuilder()

        for material in self.field_substrate.materials():
            builder.add_substrate_material(material)

        for material in self.field_inclusion.materials():
            builder.add_inclusion_material(material)

        for diameter_m in self.field_diameter.diameters_m():
            builder.add_inclusion_diameter_m(diameter_m)

        for tilt_deg in self.field_tilt.tilts_deg():
            builder.add_tilt_deg(tilt_deg)

        for rotation_deg in self.field_rotation.rotations_deg():
            builder.add_rotation_deg(rotation_deg)

        return super().samples() + builder.build()

def run(): #pragma: no cover
    import sys
    app = QtWidgets.QApplication(sys.argv)

    table = InclusionSampleWidget()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
