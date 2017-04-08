""""""

# Standard library modules.
import math

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo.options.detector.photon import PhotonDetector, PhotonDetectorBuilder

from pymontecarlo_gui.widgets.field import Field, FieldLayout
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.util.tolerance import tolerance_to_decimals
from pymontecarlo_gui.options.detector.base import DetectorWidget

# Globals and constants variables.

class ElevationField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Elevations [\u00b0]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(PhotonDetector.ELEVATION_TOLERANCE_rad))
        self._widget.setRange(-90.0, 90.0, decimals)
        self._widget.setValues([40.0])

        # Signals
        self._widget.valuesChanged.connect(self.changed)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def elevationsDegree(self):
        return self._widget.values()

    def setElevationsDegree(self, tilts_deg):
        self._widget.setValues(tilts_deg)

class AzimuthField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Azimuths [\u00b0]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(PhotonDetector.AZIMUTH_TOLERANCE_rad))
        self._widget.setRange(0.0, 360.0, decimals)
        self._widget.setValues([0.0])

        # Signals
        self._widget.valuesChanged.connect(self.changed)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def azimuthsDegree(self):
        return self._widget.values()

    def setAzimuthsDegree(self, tilts_deg):
        self._widget.setValues(tilts_deg)

class PhotonDetectorWidget(DetectorWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # widgets
        self.field_elevation = ElevationField()

        self.field_azimuth = AzimuthField()

        # Layouts
        layout = FieldLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLabelField(self.field_elevation)
        layout.addLabelField(self.field_azimuth)
        self.setLayout(layout)

        # Signals
        self.field_elevation.changed.connect(self.changed)
        self.field_azimuth.changed.connect(self.changed)

    def isValid(self):
        return super().isValid() and \
            self.field_elevation.isValid() and \
            self.field_azimuth.isValid()

    def detectors(self):
        builder = PhotonDetectorBuilder()

        for elevation_deg in self.field_elevation.elevationsDegree():
            builder.add_elevation_deg(elevation_deg)

        for azimuth_deg in self.field_azimuth.azimuthsDegree():
            builder.add_azimuth_deg(azimuth_deg)

        return super().detectors() + builder.build()
