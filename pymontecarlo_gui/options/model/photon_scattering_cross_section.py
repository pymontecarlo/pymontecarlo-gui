"""
Photon scattering cross section models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.model.base import ModelFieldBase

# Globals and constants variables.

class PhotonScatteringCrossSectionModelField(ModelFieldBase):

    def title(self):
        return 'Photon scattering cross section'
