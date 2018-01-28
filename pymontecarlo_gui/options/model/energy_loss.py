"""
Energy loss models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelFieldBase

# Globals and constants variables.

class EnergyLossModelField(ModelFieldBase):

    def title(self):
        return 'Energy loss'
