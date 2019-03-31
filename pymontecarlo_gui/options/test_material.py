#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest
from qtpy import QtCore, QtGui

# Local modules.
from pymontecarlo_gui.options.material import \
    (FormulaValidator, MaterialPureWidget, MaterialFormulaWidget,
     MaterialAdvancedWidget, MaterialListWidget)
from pymontecarlo_gui.util.testutil import checkbox_click
from pymontecarlo.options.material import Material
from pymontecarlo.options.composition import generate_name, calculate_density_kg_per_m3

# Globals and constants variables.

@pytest.fixture
def formula_validator():
    return FormulaValidator()

def test_formula_validate_acceptable(formula_validator):
    state, text, pos = formula_validator.validate("Al2O3", 5)
    assert state == QtGui.QValidator.Acceptable
    assert text == 'Al2O3'
    assert pos == 5

def test_formula_validate_intermediate(formula_validator):
    state, text, pos = formula_validator.validate("A", 1)
    assert state == QtGui.QValidator.Intermediate
    assert text == 'A'
    assert pos == 1

def test_formula_validate_invalid(formula_validator):
    state, text, pos = formula_validator.validate("-", 1)
    assert state == QtGui.QValidator.Invalid
    assert text == '-'
    assert pos == 1

@pytest.fixture
def material_pure_widget():
    return MaterialPureWidget()

def test_material_pure_widget(qtbot, material_pure_widget):
    button = material_pure_widget.wdg_periodic_table._group.button(13)
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)

    button = material_pure_widget.wdg_periodic_table._group.button(29)
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)

    materials = material_pure_widget.materials()

    assert len(materials) == 2
    assert Material.pure(13) in materials
    assert Material.pure(29) in materials

def test_material_pure_widget2(qtbot, material_pure_widget):
    button = material_pure_widget.wdg_periodic_table._group.button(13)
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)

    button = material_pure_widget.wdg_periodic_table._group.button(13)
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)

    materials = material_pure_widget.materials()
    assert not materials

@pytest.fixture
def material_formula_widget():
    return MaterialFormulaWidget()

def test_material_formula_widget_nomaterials(qtbot, material_formula_widget):
    widget = material_formula_widget.field_formula.widget()
    qtbot.keyClicks(widget, "A")

    materials = material_formula_widget.materials()

    assert not materials

def test_material_formula_widget_auto_density(qtbot, material_formula_widget):
    widget = material_formula_widget.field_formula.widget()
    qtbot.keyClicks(widget, "Al")

    materials = material_formula_widget.materials()

    assert len(materials) == 1
    assert materials[0].density_kg_per_m3 == pytest.approx(Material.pure(13).density_kg_per_m3, abs=1e-4)

def test_material_formula_widget_user_density(qtbot, material_formula_widget):
    widget = material_formula_widget.field_formula.widget()
    qtbot.keyClicks(widget, "Al")

    widget = material_formula_widget.field_density.suffixWidget()
    checkbox_click(qtbot, widget)

    widget = material_formula_widget.field_density.widget()
    widget.clear()
    qtbot.keyClicks(widget, "9")

    materials = material_formula_widget.materials()

    assert len(materials) == 1
    assert materials[0].density_kg_per_m3 == pytest.approx(9000, abs=1e-4)

@pytest.fixture
def material_advanced_widget():
    return MaterialAdvancedWidget()

def test_material_advanced_widget_nomaterials(qtbot, material_advanced_widget):
    materials = material_advanced_widget.materials()

    assert not materials

def test_material_advanced_widget_auto(qtbot, material_advanced_widget):
    material_advanced_widget.tbl_composition.setComposition({13: 1.0})

    materials = material_advanced_widget.materials()

    assert len(materials) == 1

    material = materials[0]

    assert material.name == generate_name({13: 1.0})
    assert material.composition == {13: 1.0}
    assert material.density_kg_per_m3 == pytest.approx(calculate_density_kg_per_m3({13: 1.0}), abs=1e-4)

def test_material_advanced_widget_user(qtbot, material_advanced_widget):
    widget = material_advanced_widget.field_name.suffixWidget()
    checkbox_click(qtbot, widget)

    widget = material_advanced_widget.field_name.widget()
    widget.clear()
    qtbot.keyClicks(widget, "foo")

    material_advanced_widget.tbl_composition.setComposition({13: 1.0})

    widget = material_advanced_widget.field_density.suffixWidget()
    checkbox_click(qtbot, widget)

    widget = material_advanced_widget.field_density.widget()
    widget.clear()
    qtbot.keyClicks(widget, "9")

    materials = material_advanced_widget.materials()

    assert len(materials) == 1

    material = materials[0]

    assert material.name == 'foo'
    assert material.composition == {13: 1.0}
    assert material.density_kg_per_m3 == pytest.approx(9000, abs=1e-4)

def test_material_advanced_widget_setMaterial(qtbot, material_advanced_widget):
    material = Material('foo', {13: 1.0}, 9000)
    material_advanced_widget.setMaterial(material)

    widget = material_advanced_widget.field_name.suffixWidget()
    assert not widget.isChecked()

    widget = material_advanced_widget.field_name.widget()
    assert widget.text() == material.name

    widget = material_advanced_widget.field_density.suffixWidget()
    assert widget.isChecked()

    widget = material_advanced_widget.field_density.widget()
    assert widget.value() == pytest.approx(material.density_g_per_cm3, abs=1e-4)

    composition = material_advanced_widget.tbl_composition.composition()
    assert composition == material.composition

    materials = material_advanced_widget.materials()

    assert len(materials) == 1
    assert materials[0] == material

@pytest.fixture
def material_list_widget(materials):
    widget = MaterialListWidget()
    widget.setMaterials(materials)
    return widget

def test_material_list_widget_selectedMaterials(material_list_widget):
    assert not material_list_widget.selectedMaterials()

def test_material_list_widget_selectedMaterials_single(material_list_widget):
    material = material_list_widget.material(0)
    material_list_widget.setSelectedMaterials([material])

    selected_materials = material_list_widget.selectedMaterials()
    assert len(selected_materials) == 1
    assert material in selected_materials

def test_material_list_widget_selectedMaterials_remove(material_list_widget):
    material = material_list_widget.material(0)
    material_list_widget.setSelectedMaterials([material])

    material_list_widget.removeMaterial(material)
    assert len(material_list_widget.materials()) == 2
    assert not material_list_widget.selectedMaterials()

def test_material_list_widget_selectedMaterials_add(material_list_widget):
    material = material_list_widget.material(0)
    material_list_widget.setSelectedMaterials([material])

    newmaterial = Material.pure(28)
    material_list_widget.addMaterial(newmaterial)
    assert newmaterial in material_list_widget.materials()

    selected_materials = material_list_widget.selectedMaterials()
    assert len(selected_materials) == 1
    assert material in selected_materials
