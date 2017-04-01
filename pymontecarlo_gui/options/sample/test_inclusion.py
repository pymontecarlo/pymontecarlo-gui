#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleWidget

# Globals and constants variables.

class TestInclusionSampleWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = InclusionSampleWidget()

    def testsamples(self):
        materials = self.create_materials()
        self.wdg.setAvailableMaterials(materials)

        widget = self.wdg.field_substrate.widget()
        widget.setSelectedMaterials(materials[:2])

        widget = self.wdg.field_inclusion.widget()
        widget.setSelectedMaterials(materials[-2:])

        widget = self.wdg.field_diameter.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '100.0;200.0')

        widget = self.wdg.field_tilt.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.wdg.field_rotation.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '3.3;4.4')

        samples = self.wdg.samples()
        self.assertEqual(2 ** 5, len(samples))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
