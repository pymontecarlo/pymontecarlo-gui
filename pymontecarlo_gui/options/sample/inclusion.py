""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo.options.sample.inclusion import InclusionSample, InclusionSampleBuilder

from pymontecarlo_gui.options.sample.base import \
    SampleField, AngleField, MaterialWidgetField, DiameterField

# Globals and constants variables.

class SubstrateField(MaterialWidgetField):

    def title(self):
        return 'Substrate'

class InclusionField(MaterialWidgetField):

    def __init__(self):
        super().__init__()

        self.field_diameter = DiameterField()
        self.field_diameter.setTolerance(InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)
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
