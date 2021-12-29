""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

INVALID_COLOR = "pink"

VALID_BACKGROUND_STYLESHEET = "background: none"
INVALID_BACKGROUND_STYLESHEET = "background: " + INVALID_COLOR


class ValidableBase:
    def isValid(self):
        return True
