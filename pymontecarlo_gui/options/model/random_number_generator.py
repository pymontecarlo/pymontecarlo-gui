"""
Random number generator models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelFieldBase

# Globals and constants variables.


class RandomNumberGeneratorModelField(ModelFieldBase):
    def title(self):
        return "Random number generator"
