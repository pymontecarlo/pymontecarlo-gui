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
        self.setAccessibleName('Inclusion')
        self.setAccessibleDescription('An half-sphere inclusion in a substrate')

        # Widgets
        self.field_substrate = SubstrateMaterialField()

        self.field_inclusion = InclusionMaterialField()

        self.field_diameter = InclusionDiameterField()

        self.field_tilt = TiltField()

        self.field_rotation = RotationField()

        # Layouts
        layout = FieldLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addGroupField(self.field_substrate)
        layout.addGroupField(self.field_inclusion)
        layout.addLabelField(self.field_diameter)
        layout.addLabelField(self.field_tilt)
        layout.addLabelField(self.field_rotation)
        self.setLayout(layout)

        # Signals
        self.field_substrate.changed.connect(self.changed)
        self.field_inclusion.changed.connect(self.changed)
        self.field_diameter.changed.connect(self.changed)
        self.field_tilt.changed.connect(self.changed)
        self.field_rotation.changed.connect(self.changed)

    def isValid(self):
        return super().isValid() and \
            self.field_substrate.isValid() and \
            self.field_inclusion.isValid() and \
            self.field_diameter.isValid() and \
            self.field_tilt.isValid() and \
            self.field_rotation.isValid()

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
