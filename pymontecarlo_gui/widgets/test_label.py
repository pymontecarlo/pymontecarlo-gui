#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtGui

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.widgets.label import LabelIcon

# Globals and constants variables.

class TestLabelIcon(TestCase):

    def setUp(self):
        super().setUp()

        self.w = LabelIcon('hello', QtGui.QIcon.fromTheme('dialog-error'))

    def testtext(self):
        self.assertEqual('hello', self.w.text())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
