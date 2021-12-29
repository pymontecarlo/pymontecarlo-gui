#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo_gui.options.sample.horizontallayers import HorizontalLayerSampleField
from pymontecarlo.options.sample.base import LayerBuilder

# Globals and constants variables.


@pytest.fixture
def horizontal_layer_sample_field():
    return HorizontalLayerSampleField()


def test_horizontal_layer_sample_field(qtbot, horizontal_layer_sample_field, materials):
    horizontal_layer_sample_field.setAvailableMaterials(materials)

    builder = LayerBuilder()
    builder.add_material(materials[0])
    builder.add_material(materials[1])
    builder.add_thickness_m(10.0)
    widget = horizontal_layer_sample_field.field_layers.widget()
    widget.setLayerBuilders([builder])

    widget = horizontal_layer_sample_field.field_substrate.field_material.widget()
    widget.setSelectedMaterials(materials[:2])

    widget = horizontal_layer_sample_field.field_angle.field_tilt.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "1.1;2.2")

    widget = horizontal_layer_sample_field.field_angle.field_azimuth.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "3.3;4.4")

    samples = horizontal_layer_sample_field.samples()
    assert len(samples) == 2 ** 4
