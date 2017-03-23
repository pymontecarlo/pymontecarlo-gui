#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtTest, QtGui, QtCore

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.widgets.lineedit import ColoredLineEdit

# Globals and constants variables.

class TestColoredLineEdit(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = ColoredLineEdit()
        self.wdg.setValidator(QtGui.QIntValidator(10, 50))

    def testsetText(self):
        self.wdg.setText('33')
        self.assertEqual('background: none', self.wdg.styleSheet())

        self.wdg.setText('0')
        self.assertEqual('background: pink', self.wdg.styleSheet())

    def testenter_text(self):
        QtTest.QTest.mouseClick(self.wdg, QtCore.Qt.LeftButton)
        QtTest.QTest.keyPress(self.wdg, QtCore.Qt.Key_3)
        self.assertEqual('3', self.wdg.text())
        self.assertEqual('background: pink', self.wdg.styleSheet())

        QtTest.QTest.keyPress(self.wdg, QtCore.Qt.Key_3)
        self.assertEqual('33', self.wdg.text())
        self.assertEqual('background: none', self.wdg.styleSheet())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
