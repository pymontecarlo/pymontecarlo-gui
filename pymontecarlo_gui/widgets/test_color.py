#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest
from qtpy import QtCore

# Local modules.
from pymontecarlo_gui.widgets.color import ColorButton, ColorDialogButton

# Globals and constants variables.

@pytest.mark.parametrize('color',
    ['#ff0000', (1.0, 0.0, 0.0), (1.0, 0.0, 0.0, 1.0), 'red'])
def test_color_button(qtbot, color):
    button = ColorButton()
    button.setColor(color)
    assert button.color() == QtCore.Qt.red
    assert button.rgba() == (1.0, 0.0, 0.0, 1.0)

@pytest.fixture
def color_dialog_button():
    return ColorDialogButton()

def test_color_dialog_button_clicked(qtbot, color_dialog_button):
    qtbot.mouseClick(color_dialog_button, QtCore.Qt.LeftButton)

def test_color_dialog_button_color(color_dialog_button):
    color = QtCore.Qt.red
    color_dialog_button.setColor(color)
    assert color_dialog_button.color() == color
