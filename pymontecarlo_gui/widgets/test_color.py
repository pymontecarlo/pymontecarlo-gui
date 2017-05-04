#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtCore, QtTest

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.widgets.color import ColorButton, ColorDialogButton

# Globals and constants variables.

class TestColorButton(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = ColorButton()

    def testcolor_globalcolor(self):
        self.wdg.setColor(QtCore.Qt.red)
        self.assertEqual(QtCore.Qt.red, self.wdg.color())
        self.assertTupleEqual((1.0, 0.0, 0.0, 1.0), self.wdg.rgba())

    def testcolor_hex(self):
        self.wdg.setColor('#ff0000')
        self.assertEqual(QtCore.Qt.red, self.wdg.color())
        self.assertTupleEqual((1.0, 0.0, 0.0, 1.0), self.wdg.rgba())

    def testcolor_rgb(self):
        self.wdg.setColor((1.0, 0.0, 0.0))
        self.assertEqual(QtCore.Qt.red, self.wdg.color())
        self.assertTupleEqual((1.0, 0.0, 0.0, 1.0), self.wdg.rgba())

    def testcolor_rgba(self):
        self.wdg.setColor((1.0, 0.0, 0.0, 1.0))
        self.assertEqual(QtCore.Qt.red, self.wdg.color())
        self.assertTupleEqual((1.0, 0.0, 0.0, 1.0), self.wdg.rgba())

    def testcolor_html(self):
        self.wdg.setColor('red')
        self.assertEqual(QtCore.Qt.red, self.wdg.color())
        self.assertTupleEqual((1.0, 0.0, 0.0, 1.0), self.wdg.rgba())

class TestColorDialogButton(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = ColorDialogButton()

    def testskeleton(self):
        color = QtCore.Qt.red
        self.wdg.setColor(color)
        self.assertEqual(color, self.wdg.color())

    def testclicked(self):
        QtTest.QTest.mouseClick(self.wdg, QtCore.Qt.LeftButton)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
