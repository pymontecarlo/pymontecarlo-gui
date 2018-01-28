""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtWidgets

import numpy as np

# Local modules.
from pymontecarlo.options.beam.base import BeamBase
from pymontecarlo.options.particle import Particle
from pymontecarlo.util.tolerance import tolerance_to_decimals

from pymontecarlo_gui.widgets.field import MultiValueFieldBase, FieldBase, WidgetFieldBase
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit

# Globals and constants variables.

class EnergyField(MultiValueFieldBase):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(BeamBase.ENERGY_TOLERANCE_eV) + 3
        self._widget.setRange(0, 1000, decimals)
        self._widget.setValues([20.0])

        # Signals
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Energies [keV]'

    def widget(self):
        return self._widget

    def energiesEV(self):
        return np.array(self._widget.values()) * 1e3

    def setEnergiesEV(self, energies_eV):
        energies_eV = np.array(energies_eV) / 1e3
        self._widget.setValues(energies_eV)

class ParticleField(FieldBase):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = QtWidgets.QComboBox()

        for particle in Particle:
            self._widget.addItem(particle.name, particle)

        index = self._widget.findData(Particle.ELECTRON)
        self._widget.setCurrentIndex(index)

        # Signals
        self._widget.currentIndexChanged.connect(self.fieldChanged)

    def title(self):
        return 'Particle'

    def widget(self):
        return self._widget

    def particle(self):
        return self._widget.currentData()

    def setParticle(self, particle):
        index = self._widget.findData(particle)
        self._widget.setCurrentIndex(index)

class BeamFieldBase(WidgetFieldBase):

    def isValid(self):
        return super().isValid() and bool(self.beams())

    @abc.abstractmethod
    def beams(self):
        """
        Returns a :class:`list` of :class:`BeamBase`.
        """
        return []

