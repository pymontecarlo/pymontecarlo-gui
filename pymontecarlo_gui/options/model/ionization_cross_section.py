"""
Ionization cross section models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelFieldBase

# Globals and constants variables.


class IonizationCrossSectionModelField(ModelFieldBase):
    def title(self):
        return "Ionization cross section"
