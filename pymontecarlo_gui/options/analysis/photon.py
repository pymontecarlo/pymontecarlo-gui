""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.options.analysis.base import AnalysisWidget

# Globals and constants variables.

class PhotonAnalysisWidget(AnalysisWidget):

    def _register_requirements(self, toolbox):
        super()._register_requirements(toolbox)
        toolbox.registerPhotonDetectorRequirement(self)

    def _unregister_requirements(self, toolbox):
        super()._unregister_requirements(toolbox)
        toolbox.unregisterPhotonDetectorRequirement(self)
