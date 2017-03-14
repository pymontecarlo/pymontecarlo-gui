""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

def clear_stackedwidget(wdg):
    for index in reversed(range(wdg.count())):
        wdg.removeWidget(wdg.widget(index))
