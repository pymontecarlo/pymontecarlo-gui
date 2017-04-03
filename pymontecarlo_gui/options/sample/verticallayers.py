""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
from pymontecarlo.options.sample.verticallayers import \
    VerticalLayerSampleBuilder, VerticalLayerSample

from pymontecarlo_gui.options.sample.base import \
    TiltField, RotationField, MaterialField, LayerBuilderField, SampleWidget
from pymontecarlo_gui.widgets.field import FieldLayout, LabelField
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.util.tolerance import tolerance_to_decimals

# Globals and constants variables.

class LeftMaterialField(MaterialField):

    def title(self):
        return "Left material(s)"

class RightMaterialField(MaterialField):

    def title(self):
        return "Right material(s)"

class DepthField(LabelField):

    depthsChanged = QtCore.Signal(tuple)

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
        self._widget.valuesChanged.connect(self.depthsChanged)
        self._suffix.stateChanged.connect(self._on_infinite_changed)

    def _on_infinite_changed(self):
        is_infinite = self._suffix.isChecked()
        self._widget.setValues([])
        self._widget.setEnabled(not is_infinite)
        self.depthsChanged.emit((float('inf'),))

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def suffix(self):
        return self._suffix

    def depths_m(self):
        if self._suffix.isChecked():
            return (float('inf'),)
        else:
            return self._widget.values()

    def setDepths_m(self, depths_deg):
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

        # Layouts
        layout = FieldLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addField(self.field_left)
        layout.addField(self.field_layers)
        layout.addField(self.field_right)
        layout.addField(self.field_depth)
        layout.addField(self.field_tilt)
        layout.addField(self.field_rotation)
        self.setLayout(layout)

        # Signals
        self.field_left.materialsChanged.connect(self.samplesChanged)
        self.field_layers.layerBuildersChanged.connect(self.samplesChanged)
        self.field_right.materialsChanged.connect(self.samplesChanged)
        self.field_depth.depthsChanged.connect(self.samplesChanged)
        self.field_tilt.tiltsChanged.connect(self.samplesChanged)
        self.field_rotation.rotationsChanged.connect(self.samplesChanged)

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

        for depth_m in self.field_depth.depths_m():
            builder.add_depth_m(depth_m)

        for tilt_deg in self.field_tilt.tilts_deg():
            builder.add_tilt_deg(tilt_deg)

        for rotation_deg in self.field_rotation.rotations_deg():
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
