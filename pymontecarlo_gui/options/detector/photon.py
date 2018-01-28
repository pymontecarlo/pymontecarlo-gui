""""""

# Standard library modules.
import math

# Third party modules.

# Local modules.
from pymontecarlo.options.detector.photon import PhotonDetector, PhotonDetectorBuilder
from pymontecarlo.util.tolerance import tolerance_to_decimals

from pymontecarlo_gui.widgets.field import MultiValueFieldBase
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.options.detector.base import DetectorFieldBase

# Globals and constants variables.

class ElevationField(MultiValueFieldBase):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(PhotonDetector.ELEVATION_TOLERANCE_rad))
        self._widget.setRange(-90.0, 90.0, decimals)
        self._widget.setValues([40.0])

        # Signals
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Elevations [\u00b0]'

    def widget(self):
        return self._widget

    def elevationsDegree(self):
        return self._widget.values()

    def setElevationsDegree(self, tilts_deg):
        self._widget.setValues(tilts_deg)

class AzimuthField(MultiValueFieldBase):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(PhotonDetector.AZIMUTH_TOLERANCE_rad))
        self._widget.setRange(0.0, 360.0, decimals)
        self._widget.setValues([0.0])

        # Signals
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Azimuths [\u00b0]'

    def widget(self):
        return self._widget

    def azimuthsDegree(self):
        return self._widget.values()

    def setAzimuthsDegree(self, tilts_deg):
        self._widget.setValues(tilts_deg)

class PhotonDetectorField(DetectorFieldBase):

    def __init__(self):
        super().__init__()

        self.field_elevation = ElevationField()
        self.addLabelField(self.field_elevation)

        self.field_azimuth = AzimuthField()
        self.addLabelField(self.field_azimuth)

    def title(self):
        return 'Photon detector'

    def description(self):
        return 'Detector to collect emitted X-rays'

    def detectors(self):
        builder = PhotonDetectorBuilder()

        for elevation_deg in self.field_elevation.elevationsDegree():
            builder.add_elevation_deg(elevation_deg)

        for azimuth_deg in self.field_azimuth.azimuthsDegree():
            builder.add_azimuth_deg(azimuth_deg)

        return super().detectors() + builder.build()
