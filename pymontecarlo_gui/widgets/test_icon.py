#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.widgets.icon import load_icon

# Globals and constants variables.


def test_load_icon():
    icon = load_icon("newsimulation.svg")
    assert icon is not None
