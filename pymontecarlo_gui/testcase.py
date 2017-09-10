""""""

# Standard library modules.
import unittest

# Third party modules.
from qtpy import QtWidgets, QtTest, QtCore

import pkg_resources

# Local modules.
from pymontecarlo.options.material import Material
from pymontecarlo.util.entrypoint import reset_entrypoints
import pymontecarlo.testcase

from pymontecarlo_gui.util.entrypoint import ENTRYPOINT_GUI_PROGRAMS

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

class TestCase(pymontecarlo.testcase.TestCase):
    '''Helper class to provide QApplication instances'''

    qapplication = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Add program mock field
        requirement = pkg_resources.Requirement('pymontecarlo_gui')
        distribution = pkg_resources.working_set.find(requirement)

        entry_point = pkg_resources.EntryPoint('mock', 'pymontecarlo_gui.mock',
                                               attrs=('ProgramFieldMock',),
                                               dist=distribution)

        entry_map = distribution.get_entry_map()
        entry_map.setdefault(ENTRYPOINT_GUI_PROGRAMS, {})
        entry_map[ENTRYPOINT_GUI_PROGRAMS]['mock'] = entry_point

        # Reset entry points
        reset_entrypoints()

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

    def create_materials(self):
        return [Material.pure(13),
                Material.from_formula('Al2O3'),
                Material('foo', {29: 0.5, 28: 0.5}, 2.0)]
