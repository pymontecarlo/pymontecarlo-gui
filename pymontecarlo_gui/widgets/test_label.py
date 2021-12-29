#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
from qtpy import QtGui
import pytest

# Local modules.
from pymontecarlo_gui.widgets.label import LabelIcon

# Globals and constants variables.


@pytest.fixture
def label_icon():
    return LabelIcon("hello", QtGui.QIcon.fromTheme("dialog-error"))


def test_label_icon(label_icon):
    assert label_icon.text() == "hello"
