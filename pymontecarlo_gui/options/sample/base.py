""""""

# Standard library modules.
import math
import abc

# Third party modules.
from qtpy import QtWidgets, QtCore

import numpy as np

# Local modules.
from pymontecarlo.options.sample.base import Sample

from pymontecarlo_gui.widgets.field import LabelField, GroupField
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.util.tolerance import tolerance_to_decimals
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.options.material import MaterialListWidget

# Globals and constants variables.

class TiltField(LabelField):

    tiltsChanged = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Tilt(s) [\u00b0]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(Sample.TILT_TOLERANCE_rad))
        self._widget.setRange(-180.0, 180.0, decimals)
        self._widget.setValues([0.0])

        # Signals
        self._widget.valuesChanged.connect(self.tiltsChanged)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def tilts_deg(self):
        return self._widget.values()

    def setTilts_deg(self, tilts_deg):
        self._widget.setValues(tilts_deg)

class RotationField(LabelField):

    rotationsChanged = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Rotation(s) [\u00b0]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(Sample.ROTATION_TOLERANCE_rad))
        self._widget.setRange(0.0, 360.0, decimals)
        self._widget.setValues([0.0])

        # Signals
        self._widget.valuesChanged.connect(self.rotationsChanged)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def rotations_deg(self):
        return self._widget.values()

    def setRotations_deg(self, rotations_deg):
        self._widget.setValues(rotations_deg)

class MaterialField(GroupField):

    materialsChanged = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = MaterialListWidget()

        # Signals
        self._widget.selectionChanged.connect(self.materialsChanged)

    def _create_group_box(self):
        groupbox = super()._create_group_box()
        groupbox.setStyleSheet('color: blue')
        return groupbox

    def title(self):
        return 'Material(s)'

    def widget(self):
        return self._widget

    def materials(self):
        return self._widget.selectedMaterials()

    def setMaterials(self, materials):
        self._widget.setSelectedMaterials(materials)

    def availableMaterials(self):
        return self._widget.materials()

    def setAvailableMaterials(self, materials):
        self._widget.setMaterials(materials)

class DiameterField(LabelField):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Diameter(s) [nm]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        tolerance = self._get_tolerance_m()
        decimals = tolerance_to_decimals(tolerance)
        self._widget.setRange(tolerance, float('inf'), decimals)
        self._widget.setValues([100.0])

    @abc.abstractmethod
    def _get_tolerance_m(self):
        raise NotImplementedError

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def diameters_m(self):
        return np.array(self._widget.values()) * 1e-9

    def setDiameters_m(self, diameters_m):
        values = np.array(diameters_m) * 1e9
        self._widget.setValues(values)

class SampleWidget(QtWidgets.QWidget, metaclass=QABCMeta):

    def __init__(self, parent=None):
        super().__init__(parent)

    @abc.abstractmethod
    def samples(self):
        """
        Returns a :class:`list` of :class:`Sample`.
        """
        return []

    @abc.abstractmethod
    def setAvailableMaterials(self, materials):
        raise NotImplementedError
