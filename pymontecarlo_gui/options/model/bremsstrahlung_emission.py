"""
Bremsstrahlung emission models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelFieldBase

# Globals and constants variables.


class BremsstrahlungEmissionModelField(ModelFieldBase):
    def title(self):
        return "Bremsstrahlung emission"
