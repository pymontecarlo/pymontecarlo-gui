#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo_gui.options.sample.substrate import SubstrateSampleField

# Globals and constants variables.


@pytest.fixture
def substrate_sample_field():
    return SubstrateSampleField()


def test_substrate_sample_field(qtbot, substrate_sample_field, materials):
    substrate_sample_field.setAvailableMaterials(materials)

    widget = substrate_sample_field.field_material.widget()
    widget.setSelectedMaterials(materials[:2])

    widget = substrate_sample_field.field_angle.field_tilt.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "1.1;2.2")

    widget = substrate_sample_field.field_angle.field_azimuth.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "3.3;4.4")

    samples = substrate_sample_field.samples()
    assert len(samples) == 2 ** 3
