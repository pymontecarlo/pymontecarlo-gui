#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo_gui.options.detector.photon import PhotonDetectorField

# Globals and constants variables.


@pytest.fixture
def photon_detector_field():
    return PhotonDetectorField()


def test_photon_detector_field(qtbot, photon_detector_field):
    widget = photon_detector_field.field_elevation.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "1.1;2.2")

    widget = photon_detector_field.field_azimuth.widget()
    widget.clear()
    qtbot.keyClicks(widget.lineedit, "3.3;4.4")

    detectors = photon_detector_field.detectors()
    assert len(detectors) == 2 ** 2
