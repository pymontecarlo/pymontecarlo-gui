#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest, QtGui

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.widgets.lineedit import \
    ColoredLineEdit, ColoredFloatLineEdit, ColoredMultiFloatLineEdit

# Globals and constants variables.

class TestColoredLineEdit(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = ColoredLineEdit()
        self.wdg.setValidator(QtGui.QIntValidator(10, 50))

    def testinitial_state(self):
        self.assertFalse(self.wdg.hasAcceptableInput())
        self.assertEqual('background: pink', self.wdg.styleSheet())

        wdg = ColoredLineEdit()
        self.assertTrue(wdg.hasAcceptableInput())
        self.assertEqual('', wdg.styleSheet())

    def testsetText(self):
        self.wdg.setText('33')
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.styleSheet())

        self.wdg.setText('0')
        self.assertFalse(self.wdg.hasAcceptableInput())
        self.assertEqual('background: pink', self.wdg.styleSheet())

    def testenter_text(self):
        QtTest.QTest.keyClicks(self.wdg, '3')
        self.assertEqual('3', self.wdg.text())
        self.assertFalse(self.wdg.hasAcceptableInput())
        self.assertEqual('background: pink', self.wdg.styleSheet())

        QtTest.QTest.keyClicks(self.wdg, '3')
        self.assertEqual('33', self.wdg.text())
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.styleSheet())

class TestColoredFloatLineEdit(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = ColoredFloatLineEdit()
        self.wdg.setRange(10.0, 50.0, 2)

    def testsetValue(self):
        self.wdg.setValue(33)
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.lineedit.styleSheet())

        self.wdg.setValue(0)
        self.assertFalse(self.wdg.hasAcceptableInput())
        self.assertEqual('background: pink', self.wdg.lineedit.styleSheet())

    def testenter_text(self):
        QtTest.QTest.keyClicks(self.wdg, '3')
        self.assertAlmostEqual(3.0, self.wdg.value(), 4)
        self.assertFalse(self.wdg.hasAcceptableInput())
        self.assertEqual('background: pink', self.wdg.lineedit.styleSheet())

        QtTest.QTest.keyClicks(self.wdg, '3')
        self.assertAlmostEqual(33.0, self.wdg.value(), 4)
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.lineedit.styleSheet())

class TestColoredMultiFloatLineEdit(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = ColoredMultiFloatLineEdit()
        self.wdg.setRange(10.0, 50.0, 2)

    def testsetValues(self):
        self.wdg.setValues([12.0, 45.0])
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.lineedit.styleSheet())

        self.wdg.setValues([0.0, 12.0, 45.0])
        self.assertFalse(self.wdg.hasAcceptableInput())
        self.assertEqual('background: pink', self.wdg.lineedit.styleSheet())

    def testsetValues_decimals(self):
        self.wdg.setValues([12.0, 45.123456])
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.lineedit.styleSheet())

        values = self.wdg.values()
        self.assertEqual(2, len(values))
        self.assertAlmostEqual(12.0, values[0], 4)
        self.assertAlmostEqual(45.12, values[1], 4)

    def testenter_text(self):
        QtTest.QTest.keyClicks(self.wdg, '3')
        self.assertFalse(self.wdg.hasAcceptableInput())
        self.assertEqual('background: pink', self.wdg.lineedit.styleSheet())

        values = self.wdg.values()
        self.assertEqual(1, len(values))
        self.assertAlmostEqual(3.0, values[0], 4)

        QtTest.QTest.keyClicks(self.wdg, '3')
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.lineedit.styleSheet())

        values = self.wdg.values()
        self.assertEqual(1, len(values))
        self.assertAlmostEqual(33.0, values[0], 4)

        QtTest.QTest.keyClicks(self.wdg, ';12.0')
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.lineedit.styleSheet())

        values = self.wdg.values()
        self.assertEqual(2, len(values))
        self.assertAlmostEqual(12.0, values[0], 4)
        self.assertAlmostEqual(33.0, values[1], 4)

        QtTest.QTest.keyClicks(self.wdg, ';20:40:10')
        self.assertTrue(self.wdg.hasAcceptableInput())
        self.assertEqual('background: none', self.wdg.lineedit.styleSheet())

        values = self.wdg.values()
        self.assertEqual(4, len(values))
        self.assertAlmostEqual(12.0, values[0], 4)
        self.assertAlmostEqual(20.0, values[1], 4)
        self.assertAlmostEqual(30.0, values[2], 4)
        self.assertAlmostEqual(33.0, values[3], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
