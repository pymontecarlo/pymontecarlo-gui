""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

def make_italic(widget):
    font = widget.font()
    font.setItalic(True)
    widget.setFont(font)