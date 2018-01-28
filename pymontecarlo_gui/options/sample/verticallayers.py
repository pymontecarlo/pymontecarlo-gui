""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

import numpy as np

# Local modules.
from pymontecarlo.options.sample.verticallayers import \
    VerticalLayerSampleBuilder, VerticalLayerSample
from pymontecarlo.util.tolerance import tolerance_to_decimals

from pymontecarlo_gui.options.sample.base import \
    AngleField, MaterialWidgetField, LayerBuilderField, SampleFieldBase
from pymontecarlo_gui.widgets.field import MultiValueFieldBase, WidgetFieldBase
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit

# Globals and constants variables.

class LeftSubstrateField(MaterialWidgetField):

    def title(self):
        return "Left substrate"

class RightSubstrateField(MaterialWidgetField):

    def title(self):
        return "Right substrate"

class DepthField(MultiValueFieldBase):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        tolerance = VerticalLayerSample.DEPTH_TOLERANCE_m * 1e9
        decimals = tolerance_to_decimals(tolerance)
        self._widget.setRange(tolerance, float('inf'), decimals)
        self._widget.setEnabled(False)

        self._suffix = QtWidgets.QCheckBox('infinite')
        self._suffix.setChecked(True)

        # Signals
        self._widget.valuesChanged.connect(self.fieldChanged)
        self._suffix.stateChanged.connect(self._on_infinite_changed)

    def _on_infinite_changed(self):
        is_infinite = self._suffix.isChecked()
        self._widget.setValues([])
        self._widget.setEnabled(not is_infinite)
        self.fieldChanged.emit()

    def title(self):
        return 'Depth(s) [nm]'

    def widget(self):
        return self._widget

    def suffixWidget(self):
        return self._suffix

    def isValid(self):
        if self._suffix.isChecked():
            return True
        return super().isValid()

    def depthsMeter(self):
        if self._suffix.isChecked():
            return (float('inf'),)
        else:
            return np.array(self._widget.values()) * 1e-9

    def setDepthsMeter(self, depths_m):
        values = np.array(depths_m) * 1e9
        self._widget.setValues(values)
        self._suffix.setChecked(False)

class DimensionField(WidgetFieldBase):

    def __init__(self):
        super().__init__()

        self.field_depth = DepthField()
        self.addLabelField(self.field_depth)

    def title(self):
        return 'Dimension'

    def depthsMeter(self):
        return self.field_depth.depthsMeter()

    def setDepthsMeter(self, depths_m):
        self.field_depth.setDepthsMeter(depths_m)

class VerticalLayerSampleField(SampleFieldBase):

    def __init__(self):
        super().__init__()

        self.field_left = LeftSubstrateField()
        self.addField(self.field_left)

        self.field_layers = LayerBuilderField()
        self.addField(self.field_layers)

        self.field_right = RightSubstrateField()
        self.addField(self.field_right)

        self.field_dimension = DimensionField()
        self.addField(self.field_dimension)

        self.field_angle = AngleField()
        self.addField(self.field_angle)

    def title(self):
        return 'Vertical layered sample'

    def description(self):
        return 'YZ planes sandwiched between two infinite substrates'

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

        for depth_m in self.field_dimension.depthsMeter():
            builder.add_depth_m(depth_m)

        for tilt_deg in self.field_angle.tiltsDegree():
            builder.add_tilt_deg(tilt_deg)

        for azimuth_deg in self.field_angle.azimuthsDegree():
            builder.add_azimuth_deg(azimuth_deg)

        return super().samples() + builder.build()

def run(): #pragma: no cover
    import sys

    app = QtWidgets.QApplication(sys.argv)

    field = VerticalLayerSampleField()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(field.widget())
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
