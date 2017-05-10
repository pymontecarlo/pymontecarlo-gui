""""""

# Standard library modules.
import os
import pkgutil

# Third party modules.
from qtpy import QtGui

# Local modules.

# Globals and constants variables.

def load_pixmap(filename):
    package = 'pymontecarlo_gui'
    resource = os.path.join('icons', filename)
    data = pkgutil.get_data(package, resource)

    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(data)

    return pixmap

def load_icon(filename):
    pixmap = load_pixmap(filename)
    return QtGui.QIcon(pixmap)
