""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
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
        self.field_substrate = SubstrateMaterialField()

        self.field_tilt = TiltField()

        self.field_rotation = RotationField()

        # Layouts
        layout = QtWidgets.QGridLayout()
        self.field_substrate.addToGridLayout(layout, 0)
        self.field_tilt.addToGridLayout(layout, 1)
        self.field_rotation.addToGridLayout(layout, 2)
        self.setLayout(layout)

    def availableMaterials(self):
        return self.field_substrate.materials()

    def setAvailableMaterials(self, materials):
        self.field_substrate.setMaterials(materials)

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
