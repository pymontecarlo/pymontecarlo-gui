""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.


class ToleranceMixin:

    DEFAULT_TOLERANCE = 1e-12

    def toleranceMeter(self):
        if not hasattr(self, "_tolerance_m"):
            self._tolerance_m = self.DEFAULT_TOLERANCE
        return self._tolerance_m

    def setToleranceMeter(self, tolerance_m):
        self._tolerance_m = tolerance_m
