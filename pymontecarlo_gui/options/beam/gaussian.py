""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.beam.gaussian import GaussianBeamBuilder

from pymontecarlo_gui.options.beam.cylindrical import CylindricalBeamField

# Globals and constants variables.


class GaussianBeamField(CylindricalBeamField):
    def title(self):
        return "Gaussian beam"

    def description(self):
        return "Incident particles distributed following a 2D-Gaussian distribution"

    def _create_builder(self):
        return GaussianBeamBuilder()
