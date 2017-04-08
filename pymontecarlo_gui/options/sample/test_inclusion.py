#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleField

# Globals and constants variables.

class TestInclusionSampleWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.field = InclusionSampleField()

    def testsamples(self):
        materials = self.create_materials()
        self.field.setAvailableMaterials(materials)

        widget = self.field.field_substrate.field_material.widget()
        widget.setSelectedMaterials(materials[:2])

        widget = self.field.field_inclusion.field_material.widget()
        widget.setSelectedMaterials(materials[-2:])

        widget = self.field.field_inclusion.field_diameter.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '100.0;200.0')

        widget = self.field.field_angle.field_tilt.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.field.field_angle.field_rotation.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '3.3;4.4')

        samples = self.field.samples()
        self.assertEqual(2 ** 5, len(samples))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
