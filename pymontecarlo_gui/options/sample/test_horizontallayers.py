#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.options.sample.horizontallayers import HorizontalLayerSampleField
from pymontecarlo.options.sample.base import LayerBuilder

# Globals and constants variables.

class TestHorizontalLayerSampleWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.field = HorizontalLayerSampleField()

    def testsamples(self):
        materials = self.create_materials()
        self.field.setAvailableMaterials(materials)

        builder = LayerBuilder()
        builder.add_material(materials[0])
        builder.add_material(materials[1])
        builder.add_thickness_m(10.0)
        widget = self.field.field_layers.widget()
        widget.setLayerBuilders([builder])

        widget = self.field.field_substrate.field_material.widget()
        widget.setSelectedMaterials(materials[:2])

        widget = self.field.field_angle.field_tilt.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.field.field_angle.field_rotation.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '3.3;4.4')

        samples = self.field.samples()
        self.assertEqual(2 ** 4, len(samples))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
