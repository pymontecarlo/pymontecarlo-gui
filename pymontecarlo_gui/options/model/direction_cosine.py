"""
Direction cosine models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelFieldBase

# Globals and constants variables.


class DirectionCosineModelField(ModelFieldBase):
    def title(self):
        return "Direction cosine"
