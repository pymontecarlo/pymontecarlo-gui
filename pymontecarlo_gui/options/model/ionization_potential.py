"""
Ionization potential models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelField

# Globals and constants variables.

class IonizationPotentialModelField(ModelField):

    def title(self):
        return 'Ionization potential'