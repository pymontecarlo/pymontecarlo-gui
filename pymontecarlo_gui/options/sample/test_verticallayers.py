#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleField
from pymontecarlo.options.sample.base import LayerBuilder

# Globals and constants variables.

class TestVerticalLayerSampleWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.field = VerticalLayerSampleField()

    def testsamples(self):
        materials = self.create_materials()
        self.field.setAvailableMaterials(materials)

        widget = self.field.field_left.field_material.widget()
        widget.setSelectedMaterials(materials[-2:])

        builder = LayerBuilder()
        builder.add_material(materials[0])
        builder.add_material(materials[1])
        builder.add_thickness_m(10.0)
        widget = self.field.field_layers.widget()
        widget.setLayerBuilders([builder])

        widget = self.field.field_right.field_material.widget()
        widget.setSelectedMaterials(materials[:2])

        widget = self.field.field_dimension.field_depth.suffix()
        self.checkBoxClick(widget)

        widget = self.field.field_dimension.field_depth.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.field.field_angle.field_tilt.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.field.field_angle.field_azimuth.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '3.3;4.4')

        samples = self.field.samples()
        self.assertEqual(2 ** 6, len(samples))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
