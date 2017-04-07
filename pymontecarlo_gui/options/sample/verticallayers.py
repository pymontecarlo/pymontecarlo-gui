""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo.options.sample.verticallayers import \
    VerticalLayerSampleBuilder, VerticalLayerSample

from pymontecarlo_gui.options.sample.base import \
    TiltField, RotationField, MaterialField, LayerBuilderField, SampleWidget
from pymontecarlo_gui.widgets.field import Field, FieldToolBox
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.util.tolerance import tolerance_to_decimals

# Globals and constants variables.

class LeftMaterialField(MaterialField):

    def label(self):
        return QtWidgets.QLabel("Left material(s)")

class RightMaterialField(MaterialField):

    def label(self):
        return QtWidgets.QLabel("Right material(s)")

class DepthField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Depth(s) [nm]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        tolerance = VerticalLayerSample.DEPTH_TOLERANCE_m * 1e9
        decimals = tolerance_to_decimals(tolerance)
        self._widget.setRange(tolerance, float('inf'), decimals)
        self._widget.setEnabled(False)

        self._suffix = QtWidgets.QCheckBox('infinite')
        self._suffix.setChecked(True)

        # Signals
        self._widget.valuesChanged.connect(self.changed)
        self._suffix.stateChanged.connect(self._on_infinite_changed)

    def _on_infinite_changed(self):
        is_infinite = self._suffix.isChecked()
        self._widget.setValues([])
        self._widget.setEnabled(not is_infinite)
        self.changed.emit()

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def suffix(self):
        return self._suffix

    def depthsMeter(self):
        if self._suffix.isChecked():
            return (float('inf'),)
        else:
            return self._widget.values()

    def setDepthsMeter(self, depths_deg):
        self._widget.setValues(depths_deg)
        self._suffix.setChecked(False)

class VerticalLayerSampleWidget(SampleWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName('Vertical layered sample')
        self.setAccessibleDescription('YZ planes sandwiched between two infinite substrates')

        # Widgets
        self.field_left = LeftMaterialField()

        self.field_layers = LayerBuilderField()

        self.field_right = RightMaterialField()

        self.field_depth = DepthField()

        self.field_tilt = TiltField()

        self.field_rotation = RotationField()

        toolbox = FieldToolBox()
        toolbox.addGroupField(self.field_left)
        toolbox.addGroupField(self.field_layers)
        toolbox.addGroupField(self.field_right)
        toolbox.addLabelFields("Angles", self.field_tilt, self.field_rotation)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(toolbox)
        self.setLayout(layout)

        # Signals
        self.field_left.changed.connect(self.changed)
        self.field_layers.changed.connect(self.changed)
        self.field_right.changed.connect(self.changed)
        self.field_depth.changed.connect(self.changed)
        self.field_tilt.changed.connect(self.changed)
        self.field_rotation.changed.connect(self.changed)

    def isValid(self):
        return super().isValid() and \
            self.field_left.isValid() and \
            self.field_layers.isValid() and \
            self.field_right.isValid() and \
            self.field_depth.isValid() and \
            self.field_tilt.isValid() and \
            self.field_rotation.isValid()

    def setAvailableMaterials(self, materials):
        self.field_left.setAvailableMaterials(materials)
        self.field_layers.setAvailableMaterials(materials)
        self.field_right.setAvailableMaterials(materials)

    def samples(self):
        builder = VerticalLayerSampleBuilder()

        for material in self.field_left.materials():
            builder.add_left_material(material)

        for layer_builder in self.field_layers.layerBuilders():
            builder.add_layer_builder(layer_builder)

        for material in self.field_right.materials():
            builder.add_right_material(material)

        for depth_m in self.field_depth.depthsMeter():
            builder.add_depth_m(depth_m)

        for tilt_deg in self.field_tilt.tiltsDegree():
            builder.add_tilt_deg(tilt_deg)

        for rotation_deg in self.field_rotation.rotationsDegree():
            builder.add_rotation_deg(rotation_deg)

        return super().samples() + builder.build()

def run(): #pragma: no cover
    import sys

    app = QtWidgets.QApplication(sys.argv)

    table = VerticalLayerSampleWidget()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
