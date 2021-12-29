""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.substrate import SubstrateSampleBuilder

from pymontecarlo_gui.options.sample.base import (
    SampleFieldBase,
    AngleField,
    MaterialField,
)

# Globals and constants variables.


class SubstrateSampleField(SampleFieldBase):
    def __init__(self):
        super().__init__()

        self.field_material = MaterialField()
        self.addField(self.field_material)

        self.field_angle = AngleField()
        self.addField(self.field_angle)

    def title(self):
        return "Substrate"

    def description(self):
        return "An infinitely thick sample"

    def setAvailableMaterials(self, materials):
        self.field_material.setAvailableMaterials(materials)
        self.field_material.setMaterials(materials)

    def samples(self):
        builder = SubstrateSampleBuilder()

        for material in self.field_material.materials():
            builder.add_material(material)

        for tilt_deg in self.field_angle.tiltsDegree():
            builder.add_tilt_deg(tilt_deg)

        for azimuth_deg in self.field_angle.azimuthsDegree():
            builder.add_azimuth_deg(azimuth_deg)

        return super().samples() + builder.build()


def run():  # pragma: no cover
    import sys
    from qtpy import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    field = SubstrateSampleField()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(field.widget())
    mainwindow.show()

    app.exec_()


if __name__ == "__main__":  # pragma: no cover
    run()
