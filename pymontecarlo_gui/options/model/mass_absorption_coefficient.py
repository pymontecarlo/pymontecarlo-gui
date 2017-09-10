"""
Mass absorption coefficient models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelField

# Globals and constants variables.

class MassAbsorptionCoefficientModelField(ModelField):

    def title(self):
        return 'Mass absorption coefficient'
