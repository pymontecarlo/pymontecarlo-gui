""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo.options.sample.substrate import SubstrateSampleBuilder

from pymontecarlo_gui.options.sample.base import \
    SampleWidget, TiltField, RotationField, MaterialField

# Globals and constants variables.

class SubstrateMaterialField(MaterialField):

    def title(self):
        return 'Substrate material(s)'

class SubstrateSampleWidget(SampleWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.field_material = SubstrateMaterialField()

        self.field_tilt = TiltField()

        self.field_rotation = RotationField()

        # Layouts
        layout = QtWidgets.QGridLayout()
        self.field_material.addToGridLayout(layout, 0)
        self.field_tilt.addToGridLayout(layout, 1)
        self.field_rotation.addToGridLayout(layout, 2)
        self.setLayout(layout)

    def availableMaterials(self):
        return self.field_material.availableMaterials()

    def setAvailableMaterials(self, materials):
        self.field_material.setAvailableMaterials(materials)

    def samples(self):
        builder = SubstrateSampleBuilder()

        for material in self.field_material.materials():
            builder.add_material(material)

        for tilt_deg in self.field_tilt.tilts_deg():
            builder.add_tilt_deg(tilt_deg)

        for rotation_deg in self.field_rotation.rotations_deg():
            builder.add_rotation_deg(rotation_deg)

        return super().samples() + builder.build()

def run(): #pragma: no cover
    import sys
    app = QtWidgets.QApplication(sys.argv)

    table = SubstrateSampleWidget()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
