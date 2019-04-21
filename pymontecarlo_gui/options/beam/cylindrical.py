""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

import numpy as np

# Local modules.
from pymontecarlo.options.beam.cylindrical import CylindricalBeam, CylindricalBeamBuilder
from pymontecarlo.util.tolerance import tolerance_to_decimals

from pymontecarlo_gui.options.beam.base import BeamFieldBase, EnergyField, ParticleField, PositionsField, SinglePositionField, LineScanXPositionField, LineScanYPositionField, GridPositionField
from pymontecarlo_gui.options.base import ToleranceMixin
from pymontecarlo_gui.widgets.field import MultiValueFieldBase
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit

# Globals and constants variables.

class DiameterField(MultiValueFieldBase, ToleranceMixin):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        self._widget.setValues([100.0])

        # Widgets
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Diameter(s) FWHM [nm]'

    def description(self):
        return 'The diameter corresponds to the full width at half maximum (FWHM) of a two dimensional Gaussian distribution'

    def widget(self):
        return self._widget

    def setToleranceMeter(self, tolerance_m):
        super().setToleranceMeter(tolerance_m)
        decimals = tolerance_to_decimals(tolerance_m * 1e9)
        self._widget.setRange(tolerance_m, float('inf'), decimals)

    def diametersMeter(self):
        return np.array(self._widget.values()) * 1e-9

    def setDiametersMeter(self, diameters_m):
        values = np.array(diameters_m) * 1e9
        self._widget.setValues(values)

class CylindricalBeamField(BeamFieldBase):

    def __init__(self):
        super().__init__()

        self.field_energy = EnergyField()
        self.addLabelField(self.field_energy)

        self.field_particle = ParticleField()
        self.addLabelField(self.field_particle)

        self.field_diameter = DiameterField()
        self.field_diameter.setToleranceMeter(CylindricalBeam.DIAMETER_TOLERANCE_m)
        self.field_diameter.setDiametersMeter([10e-9])
        self.addLabelField(self.field_diameter)

        self.field_position = PositionsField()
        self.field_position.setToleranceMeter(CylindricalBeam.POSITION_TOLERANCE_m)
        self.field_position.registerPositionField(SinglePositionField())
        self.field_position.registerPositionField(LineScanXPositionField())
        self.field_position.registerPositionField(LineScanYPositionField())
        self.field_position.registerPositionField(GridPositionField())

        self.addGroupField(self.field_position)

    def title(self):
        return 'Cylindrical beam'

    def description(self):
        return 'Incident particles distributed randomly within a circle'

    def _create_builder(self):
        return CylindricalBeamBuilder()

    def beams(self):
        builder = self._create_builder()

        for energy_eV in self.field_energy.energiesEV():
            builder.add_energy_eV(energy_eV)

        builder.add_particle(self.field_particle.particle())

        for diameter_m in self.field_diameter.diametersMeter():
            builder.add_diameter_m(diameter_m)

        for position in self.field_position.positions():
            builder.add_position(position.x_m, position.y_m)

        return super().beams() + builder.build()
