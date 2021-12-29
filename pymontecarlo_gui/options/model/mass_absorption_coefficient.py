"""
Mass absorption coefficient models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelFieldBase

# Globals and constants variables.


class MassAbsorptionCoefficientModelField(ModelFieldBase):
    def title(self):
        return "Mass absorption coefficient"
