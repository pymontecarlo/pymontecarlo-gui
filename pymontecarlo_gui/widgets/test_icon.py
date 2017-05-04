#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.widgets.icon import load_icon

# Globals and constants variables.

class Testicon(TestCase):

    def testload_icon(self):
        load_icon('newsimulation.svg')

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
