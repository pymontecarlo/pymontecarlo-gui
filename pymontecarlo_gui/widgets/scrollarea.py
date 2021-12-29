""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.

# Globals and constants variables.


def create_scroll_area(*widgets_or_layouts, direction=None):
    if direction is None:
        direction = QtWidgets.QBoxLayout.TopToBottom

    layout = QtWidgets.QBoxLayout(direction)
    layout.setContentsMargins(0, 0, 0, 0)

    for item in widgets_or_layouts:
        if isinstance(item, QtWidgets.QWidget):
            layout.addWidget(item)
        elif isinstance(item, QtWidgets.QLayout):
            layout.addLayout(item)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)

    area = QtWidgets.QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(widget)

    return area
