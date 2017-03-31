""""""

# Standard library modules.
import unittest

# Third party modules.
from qtpy import QtWidgets, QtTest, QtCore

# Local modules.

# Globals and constants variables.

_instance = None

class TestCase(unittest.TestCase):
    '''Helper class to provide QApplication instances'''

    qapplication = True

    def setUp(self):
        super().setUp()
        global _instance
        if _instance is None:
            _instance = QtWidgets.QApplication([])

        self.app = _instance

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.app
        super().tearDown()

    def checkBoxClick(self, checkbox):
        QtTest.QTest.mouseClick(checkbox, QtCore.Qt.LeftButton,
                                pos=QtCore.QPoint(2, checkbox.height() / 2))
