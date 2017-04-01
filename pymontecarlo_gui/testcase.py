""""""

# Standard library modules.
import unittest

# Third party modules.
from qtpy import QtWidgets, QtTest, QtCore

# Local modules.

# Globals and constants variables.

_instance = None

class MockReceiver(object):

    def __init__(self, parent=None):
        self.call_count = 0
        self.args = None

    def signalReceived(self, *args):
        self.call_count += 1
        self.args = args

    def wasCalled(self, expected_count=1):
        return self.call_count == expected_count

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

    def connectSignal(self, signal):
        receiver = MockReceiver()
        signal.connect(receiver.signalReceived)
        return receiver
