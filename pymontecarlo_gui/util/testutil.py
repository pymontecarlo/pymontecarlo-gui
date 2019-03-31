""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore

# Local modules.

# Globals and constants variables.

def checkbox_click(qtbot, checkbox):
    qtbot.mouseClick(checkbox, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, checkbox.height() / 2))