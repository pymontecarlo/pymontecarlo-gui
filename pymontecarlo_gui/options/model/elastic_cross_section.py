"""
Elastic cross section models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelField

# Globals and constants variables.

class ElasticCrossSectionModelField(ModelField):

    def title(self):
        return 'Elastic cross section'
