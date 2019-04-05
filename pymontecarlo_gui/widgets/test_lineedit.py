""" """

# Standard library modules.

# Third party modules.
import pytest
from qtpy import QtGui

# Local modules.
from pymontecarlo_gui.widgets.lineedit import \
    ColoredLineEdit, ColoredFloatLineEdit, ColoredMultiFloatLineEdit
from pymontecarlo_gui.util.validate import \
    VALID_BACKGROUND_STYLESHEET, INVALID_BACKGROUND_STYLESHEET

# Globals and constants variables.

@pytest.fixture
def coloredlineedit():
    widget = ColoredLineEdit()
    widget.setValidator(QtGui.QIntValidator(10, 50))
    return widget

def test_coloredlineedit_initial_state(qtbot, coloredlineedit):
    assert not coloredlineedit.hasAcceptableInput()
    assert coloredlineedit.styleSheet() == INVALID_BACKGROUND_STYLESHEET

    wdg = ColoredLineEdit()
    assert wdg.hasAcceptableInput()
    assert wdg.styleSheet() == ''

def test_coloredlineedit_setText(qtbot, coloredlineedit):
    coloredlineedit.setText('33')
    assert coloredlineedit.hasAcceptableInput()
    assert coloredlineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

    coloredlineedit.setText('0')
    assert not coloredlineedit.hasAcceptableInput()
    assert coloredlineedit.styleSheet() == INVALID_BACKGROUND_STYLESHEET

def test_coloredlineedit_keyClicks(qtbot, coloredlineedit):
    qtbot.keyClicks(coloredlineedit, '3')
    assert coloredlineedit.text() == '3'
    assert not coloredlineedit.hasAcceptableInput()
    assert coloredlineedit.styleSheet() == INVALID_BACKGROUND_STYLESHEET

    qtbot.keyClicks(coloredlineedit, '3')
    assert coloredlineedit.text() == '33'
    assert coloredlineedit.hasAcceptableInput()
    assert coloredlineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

@pytest.fixture
def coloredfloatlineedit():
    widget = ColoredFloatLineEdit()
    widget.setRange(10.0, 50.0, 2)
    return widget

def test_coloredfloatlineedit_setValue(qtbot, coloredfloatlineedit):
    coloredfloatlineedit.setValue(33)
    assert coloredfloatlineedit.hasAcceptableInput()
    assert coloredfloatlineedit.lineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

    coloredfloatlineedit.setValue(0)
    assert not coloredfloatlineedit.hasAcceptableInput()
    assert coloredfloatlineedit.lineedit.styleSheet() == INVALID_BACKGROUND_STYLESHEET

def test_coloredfloatlineedit_keyClicks(qtbot, coloredfloatlineedit):
    coloredfloatlineedit.clear()
    qtbot.keyClicks(coloredfloatlineedit.lineedit, '3')
    assert coloredfloatlineedit.value() == pytest.approx(3.0, abs=1e-4)
    assert not coloredfloatlineedit.hasAcceptableInput()
    assert coloredfloatlineedit.lineedit.styleSheet() == INVALID_BACKGROUND_STYLESHEET

    qtbot.keyClicks(coloredfloatlineedit.lineedit, '3')
    assert coloredfloatlineedit.value() == pytest.approx(33.0, abs=1e-4)
    assert coloredfloatlineedit.hasAcceptableInput()
    assert coloredfloatlineedit.lineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

def test_coloredfloatlineedit_valueChanged_setValue(qtbot, coloredfloatlineedit):
    with qtbot.waitSignal(coloredfloatlineedit.valueChanged) as blocker:
        coloredfloatlineedit.setValue(33)

    assert blocker.signal_triggered
    assert blocker.args[0] == pytest.approx(33.0, abs=1e-4)

def test_coloredfloatlineedit_valueChanged_keyClicks(qtbot, coloredfloatlineedit):
    coloredfloatlineedit.clear()

    with qtbot.waitSignal(coloredfloatlineedit.valueChanged) as blocker:
        qtbot.keyClicks(coloredfloatlineedit.lineedit, '3')

    assert blocker.signal_triggered
    assert blocker.args[0] == pytest.approx(3.0, abs=1e-4)

    with qtbot.waitSignal(coloredfloatlineedit.valueChanged) as blocker:
        qtbot.keyClicks(coloredfloatlineedit.lineedit, '3')

    assert blocker.signal_triggered
    assert blocker.args[0] == pytest.approx(33.0, abs=1e-4)

def test_coloredfloatlineedit_toolTip(qtbot, coloredfloatlineedit):
    assert coloredfloatlineedit.toolTip() == 'Value must be between [10.00, 50.00]'

    coloredfloatlineedit.setBottom(0.0)
    assert coloredfloatlineedit.toolTip() == 'Value must be between [0.00, 50.00]'

@pytest.fixture
def coloredmultifloatlineedit():
    widget = ColoredMultiFloatLineEdit()
    widget.setRange(10.0, 50.0, 2)
    return widget

def test_coloredmultifloatlineedit_setValues(qtbot, coloredmultifloatlineedit):
    coloredmultifloatlineedit.setValues([12.0, 45.0])
    assert coloredmultifloatlineedit.hasAcceptableInput()
    assert coloredmultifloatlineedit.lineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

    coloredmultifloatlineedit.setValues([0.0, 12.0, 45.0])
    assert not coloredmultifloatlineedit.hasAcceptableInput()
    assert coloredmultifloatlineedit.lineedit.styleSheet() == INVALID_BACKGROUND_STYLESHEET

def test_coloredmultifloatlineedit_setValues_decimals(qtbot, coloredmultifloatlineedit):
    coloredmultifloatlineedit.setValues([12.0, 45.123456])
    assert coloredmultifloatlineedit.hasAcceptableInput()
    assert coloredmultifloatlineedit.lineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

    values = coloredmultifloatlineedit.values()
    assert len(values) == 2
    assert values[0] == pytest.approx(12.0, abs=1e-4)
    assert values[1] == pytest.approx(45.12, abs=1e-4)

def test_coloredmultifloatlineedit_keyClicks(qtbot, coloredmultifloatlineedit):
    qtbot.keyClicks(coloredmultifloatlineedit.lineedit, '3')
    assert not coloredmultifloatlineedit.hasAcceptableInput()
    assert coloredmultifloatlineedit.lineedit.styleSheet() == INVALID_BACKGROUND_STYLESHEET

    values = coloredmultifloatlineedit.values()
    assert len(values) == 1
    assert values[0] == pytest.approx(3.0, abs=1e-4)

    qtbot.keyClicks(coloredmultifloatlineedit.lineedit, '3')
    assert coloredmultifloatlineedit.hasAcceptableInput()
    assert coloredmultifloatlineedit.lineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

    values = coloredmultifloatlineedit.values()
    assert len(values) == 1
    assert values[0] == pytest.approx(33.0, abs=1e-4)

    qtbot.keyClicks(coloredmultifloatlineedit.lineedit, ';12.0')
    assert coloredmultifloatlineedit.hasAcceptableInput()
    assert coloredmultifloatlineedit.lineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

    values = coloredmultifloatlineedit.values()
    assert len(values) == 2
    assert values[0] == pytest.approx(12.0, abs=1e-4)
    assert values[1] == pytest.approx(33.0, abs=1e-4)

    qtbot.keyClicks(coloredmultifloatlineedit.lineedit, ';20:40:10')
    assert coloredmultifloatlineedit.hasAcceptableInput()
    assert coloredmultifloatlineedit.lineedit.styleSheet() == VALID_BACKGROUND_STYLESHEET

    values = coloredmultifloatlineedit.values()
    assert len(values) == 4
    assert values[0] == pytest.approx(12.0, abs=1e-4)
    assert values[1] == pytest.approx(20.0, abs=1e-4)
    assert values[2] == pytest.approx(30.0, abs=1e-4)
    assert values[3] == pytest.approx(33.0, abs=1e-4)

def test_coloredmultifloatlineedit_valueChanged_setValue(qtbot, coloredmultifloatlineedit):
    with qtbot.waitSignal(coloredmultifloatlineedit.valuesChanged) as blocker:
        coloredmultifloatlineedit.setValues([33])

    assert blocker.signal_triggered
    assert blocker.args[0][0] == pytest.approx(33.0, abs=1e-4)

def test_coloredmultifloatlineedit_valueChanged_keyClicks(qtbot, coloredmultifloatlineedit):
    with qtbot.waitSignal(coloredmultifloatlineedit.valuesChanged) as blocker:
        qtbot.keyClicks(coloredmultifloatlineedit.lineedit, '3')

    assert blocker.signal_triggered
    assert blocker.args[0][0] == pytest.approx(3.0, abs=1e-4)

    with qtbot.waitSignal(coloredmultifloatlineedit.valuesChanged) as blocker:
        qtbot.keyClicks(coloredmultifloatlineedit.lineedit, '3')

    assert blocker.signal_triggered
    assert blocker.args[0][0] == pytest.approx(33.0, abs=1e-4)

def test_coloredmultifloatlineedit_toolTip(qtbot, coloredmultifloatlineedit):
    assert coloredmultifloatlineedit.toolTip() == 'Value(s) must be between [10.00, 50.00]'

    coloredmultifloatlineedit.setBottom(0.0)
    assert coloredmultifloatlineedit.toolTip() == 'Value(s) must be between [0.00, 50.00]'

