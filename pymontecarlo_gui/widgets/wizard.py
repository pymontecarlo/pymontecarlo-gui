""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

def find_wizard(widget):
    if hasattr(widget, 'wizard'):
        return widget.wizard()

    try:
        return find_wizard(widget.parent())
    except AttributeError:
        return None