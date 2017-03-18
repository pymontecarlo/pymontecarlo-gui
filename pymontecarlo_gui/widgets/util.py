""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.

def clear_stackedwidget(wdg):
    for index in reversed(range(wdg.count())):
        wdg.removeWidget(wdg.widget(index))

def create_group_box(title, *widgets, direction=None):
    if direction is None:
        direction = QtWidgets.QBoxLayout.TopToBottom

    layout = QtWidgets.QBoxLayout(direction)
    for widget in widgets:
        layout.addWidget(widget)

    box = QtWidgets.QGroupBox(title)
    box.setLayout(layout)

    return box
