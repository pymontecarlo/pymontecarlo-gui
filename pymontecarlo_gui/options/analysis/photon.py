""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.base import AnalysisField

# Globals and constants variables.

class PhotonAnalysisField(AnalysisField):

    def _register_requirements(self, toolbox):
        super()._register_requirements(toolbox)
        toolbox.registerPhotonDetectorRequirement(self)

    def _unregister_requirements(self, toolbox):
        super()._unregister_requirements(toolbox)
        toolbox.unregisterPhotonDetectorRequirement(self)
