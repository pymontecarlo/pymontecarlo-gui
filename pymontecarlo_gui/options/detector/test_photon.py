#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.options.detector.photon import PhotonDetectorField

# Globals and constants variables.

class TestPhotonDetectorField(TestCase):

    def setUp(self):
        super().setUp()

        self.field = PhotonDetectorField()

    def testsamples(self):
        widget = self.field.field_elevation.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget.lineedit, '1.1;2.2')

        widget = self.field.field_azimuth.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, '3.3;4.4')

        detectors = self.field.detectors()
        self.assertEqual(2 ** 2, len(detectors))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
