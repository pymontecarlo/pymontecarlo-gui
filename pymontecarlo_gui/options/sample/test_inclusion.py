#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleField

# Globals and constants variables.


@pytest.fixture
def inclusion_sample_field():
    return InclusionSampleField()


def test_inclusion_sample_field(qtbot, inclusion_sample_field, materials):
    inclusion_sample_field.setAvailableMaterials(materials)

    widget = inclusion_sample_field.field_substrate.field_material.widget()
    widget.setSelectedMaterials(materials[:2])

    widget = inclusion_sample_field.field_inclusion.field_material.widget()
    widget.setSelectedMaterials(materials[-2:])

    widget = inclusion_sample_field.field_inclusion.field_diameter.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "100.0;200.0")

    widget = inclusion_sample_field.field_angle.field_tilt.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "1.1;2.2")

    widget = inclusion_sample_field.field_angle.field_azimuth.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "3.3;4.4")

    samples = inclusion_sample_field.samples()
    assert len(samples) == 2 ** 5
