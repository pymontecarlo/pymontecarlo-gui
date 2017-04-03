""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.substrate import SubstrateSampleBuilder

from pymontecarlo_gui.widgets.field import FieldLayout
from pymontecarlo_gui.options.sample.base import \
    SampleWidget, TiltField, RotationField, MaterialField

# Globals and constants variables.

class SubstrateSampleWidget(SampleWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName("Substrate")
        self.setAccessibleDescription("An infinitely thick sample")

        # Widgets
        self.field_material = MaterialField()

        self.field_tilt = TiltField()

        self.field_rotation = RotationField()

        # Layouts
        layout = FieldLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addField(self.field_material)
        layout.addField(self.field_tilt)
        layout.addField(self.field_rotation)
        self.setLayout(layout)

        # Signals
        self.field_material.materialsChanged.connect(self.samplesChanged)
        self.field_tilt.tiltsChanged.connect(self.samplesChanged)
        self.field_rotation.rotationsChanged.connect(self.samplesChanged)

    def isValid(self):
        return super().isValid() and \
            self.field_material.isValid() and \
            self.field_tilt.isValid() and \
            self.field_rotation.isValid()

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
    from qtpy import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    table = SubstrateSampleWidget()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
