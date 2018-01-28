""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.base import AnalysisFieldBase

# Globals and constants variables.

class PhotonAnalysisFieldBase(AnalysisFieldBase):

    def _register_requirements(self, field_toolbox):
        super()._register_requirements(field_toolbox)
        field_toolbox.registerPhotonDetectorRequirement(self)

    def _unregister_requirements(self, field_toolbox):
        super()._unregister_requirements(field_toolbox)
        field_toolbox.unregisterPhotonDetectorRequirement(self)
