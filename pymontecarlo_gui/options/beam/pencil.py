""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo.options.beam.pencil import PencilBeam, PencilBeamBuilder

from pymontecarlo_gui.options.beam.base import (
    BeamFieldBase,
    EnergyField,
    ParticleField,
    PositionsField,
    SinglePositionField,
    LineScanXPositionField,
    LineScanYPositionField,
    GridPositionField,
)

# Globals and constants variables.


class PencilBeamField(BeamFieldBase):
    def __init__(self):
        super().__init__()

        self.field_energy = EnergyField()
        self.addLabelField(self.field_energy)

        self.field_particle = ParticleField()
        self.addLabelField(self.field_particle)

        self.field_position = PositionsField()
        self.field_position.setToleranceMeter(PencilBeam.POSITION_TOLERANCE_m)
        self.field_position.registerPositionField(SinglePositionField())
        self.field_position.registerPositionField(LineScanXPositionField())
        self.field_position.registerPositionField(LineScanYPositionField())
        self.field_position.registerPositionField(GridPositionField())

        self.addGroupField(self.field_position)

    def title(self):
        return "Pencil beam"

    def description(self):
        return "Incident particles centered at the initial position"

    def beams(self):
        builder = PencilBeamBuilder()

        for energy_eV in self.field_energy.energiesEV():
            builder.add_energy_eV(energy_eV)

        builder.add_particle(self.field_particle.particle())

        for position in self.field_position.positions():
            builder.add_position(position.x_m, position.y_m)

        return super().beams() + builder.build()
