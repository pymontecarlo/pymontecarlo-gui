"""
Special message box
"""

# Standard library modules.
import sys
import traceback
from io import StringIO

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.


def exception(
    parent,
    ex,
    buttons=QtWidgets.QMessageBox.Ok,
    defaultButton=QtWidgets.QMessageBox.NoButton,
):
    title = type(ex).__name__
    message = str(ex)
    tb = StringIO()
    if hasattr(ex, "__traceback__"):
        exc_traceback = ex.__traceback__
    else:
        exc_traceback = sys.exc_info()[2]
    traceback.print_tb(exc_traceback, file=tb)

    msgbox = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Critical, title, message, buttons, parent
    )
    msgbox.setDefaultButton(defaultButton)
    msgbox.setDetailedText(tb.getvalue())
    msgbox.exec_()
