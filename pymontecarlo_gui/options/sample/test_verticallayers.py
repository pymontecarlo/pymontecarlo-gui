#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleField
from pymontecarlo_gui.util.testutil import checkbox_click
from pymontecarlo.options.sample.base import LayerBuilder

# Globals and constants variables.


@pytest.fixture
def vertical_layer_sample_field():
    return VerticalLayerSampleField()


def test_vertical_layer_sample_field(qtbot, vertical_layer_sample_field, materials):
    vertical_layer_sample_field.setAvailableMaterials(materials)

    widget = vertical_layer_sample_field.field_left.field_material.widget()
    widget.setSelectedMaterials(materials[-2:])

    builder = LayerBuilder()
    builder.add_material(materials[0])
    builder.add_material(materials[1])
    builder.add_thickness_m(10.0)
    widget = vertical_layer_sample_field.field_layers.widget()
    widget.setLayerBuilders([builder])

    widget = vertical_layer_sample_field.field_right.field_material.widget()
    widget.setSelectedMaterials(materials[:2])

    widget = vertical_layer_sample_field.field_dimension.field_depth.suffixWidget()
    checkbox_click(qtbot, widget)

    widget = vertical_layer_sample_field.field_dimension.field_depth.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "1.1;2.2")

    widget = vertical_layer_sample_field.field_angle.field_tilt.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "1.1;2.2")

    widget = vertical_layer_sample_field.field_angle.field_azimuth.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "3.3;4.4")

    samples = vertical_layer_sample_field.samples()
    assert len(samples) == 2 ** 6
