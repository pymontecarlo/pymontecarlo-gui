"""
Layout utilities
"""

# Standard library modules.

# Third party modules.
from qtpy.QtWidgets import QFormLayout

# Local modules.

# Globals and constants variables.


def merge_formlayout(layout1, layout2):
    """
    Merge *layout2* in *layout1*.
    """
    for row in range(layout2.rowCount()):
        label = layout2.itemAt(row, QFormLayout.LabelRole)
        field = layout2.itemAt(row, QFormLayout.FieldRole)
        span = layout2.itemAt(row, QFormLayout.SpanningRole)

        if label and field:
            layout1.addRow(label.widget(), field.widget())
        elif span:
            layout1.addRow(span.widget())

    return layout1
