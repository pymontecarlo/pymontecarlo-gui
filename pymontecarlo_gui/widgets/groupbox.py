""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.

def create_group_box(title, *widgets_or_layouts, direction=None):
    if direction is None:
        direction = QtWidgets.QBoxLayout.TopToBottom

    layout = QtWidgets.QBoxLayout(direction)
    for item in widgets_or_layouts:
        if isinstance(item, QtWidgets.QWidget):
            layout.addWidget(item)
        elif isinstance(item, QtWidgets.QLayout):
            layout.addLayout(item)

    box = QtWidgets.QGroupBox(title)
    box.setLayout(layout)

    return box