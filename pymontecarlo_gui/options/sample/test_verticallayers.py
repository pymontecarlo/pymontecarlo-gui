#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleWidget
from pymontecarlo.options.sample.base import LayerBuilder

# Globals and constants variables.

class TestVerticalLayerSampleWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = VerticalLayerSampleWidget()

    def testsamples(self):
        materials = self.create_materials()
        self.wdg.setAvailableMaterials(materials)

        widget = self.wdg.field_left.widget()
        widget.setSelectedMaterials(materials[-2:])

        builder = LayerBuilder()
        builder.add_material(materials[0])
        builder.add_material(materials[1])
        builder.add_thickness_m(10.0)
        widget = self.wdg.field_layers.widget()
        widget.setLayerBuilders([builder])

        widget = self.wdg.field_right.widget()
        widget.setSelectedMaterials(materials[:2])

        widget = self.wdg.field_depth.suffix()
        self.checkBoxClick(widget)

        widget = self.wdg.field_depth.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.wdg.field_tilt.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.wdg.field_rotation.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '3.3;4.4')

        samples = self.wdg.samples()
        self.assertEqual(2 ** 6, len(samples))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
