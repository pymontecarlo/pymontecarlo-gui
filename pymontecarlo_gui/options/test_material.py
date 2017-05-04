#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from qtpy import QtCore, QtTest, QtGui

# Local modules.
from pymontecarlo_gui.testcase import TestCase
from pymontecarlo_gui.options.material import \
    (FormulaValidator, MaterialPureWidget, MaterialFormulaWidget,
     MaterialAdvancedWidget, MaterialListWidget)
from pymontecarlo.options.material import Material
from pymontecarlo.options.composition import generate_name, calculate_density_kg_per_m3

# Globals and constants variables.

class TestFormulaValidator(TestCase):

    def setUp(self):
        super().setUp()

        self.validator = FormulaValidator()

    def testvalidate_acceptable(self):
        state, text, pos = self.validator.validate("Al2O3", 5)
        self.assertEqual(QtGui.QValidator.Acceptable, state)
        self.assertEqual('Al2O3', text)
        self.assertEqual(5, pos)

    def testvalidate_intermediate(self):
        state, text, pos = self.validator.validate("A", 1)
        self.assertEqual(QtGui.QValidator.Intermediate, state)
        self.assertEqual('A', text)
        self.assertEqual(1, pos)

    def testvalidate_invalid(self):
        state, text, pos = self.validator.validate("-", 1)
        self.assertEqual(QtGui.QValidator.Invalid, state)
        self.assertEqual('-', text)
        self.assertEqual(1, pos)

class TestMaterialPureWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = MaterialPureWidget()

    def testmaterials(self):
        button = self.wdg.wdg_periodic_table._group.button(13)
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        button = self.wdg.wdg_periodic_table._group.button(29)
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        materials = self.wdg.materials()

        self.assertEqual(2, len(materials))
        self.assertIn(Material.pure(13), materials)
        self.assertIn(Material.pure(29), materials)

    def testmaterials2(self):
        button = self.wdg.wdg_periodic_table._group.button(13)
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        button = self.wdg.wdg_periodic_table._group.button(13)
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        materials = self.wdg.materials()

        self.assertEqual(0, len(materials))

class TestMaterialFormulaWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = MaterialFormulaWidget()

    def testmaterials_nomaterials(self):
        widget = self.wdg.field_formula.widget()
        QtTest.QTest.keyClicks(widget, "A")

        materials = self.wdg.materials()

        self.assertEqual(0, len(materials))

    def testmaterials_auto_density(self):
        widget = self.wdg.field_formula.widget()
        QtTest.QTest.keyClicks(widget, "Al")

        materials = self.wdg.materials()

        self.assertEqual(1, len(materials))
        self.assertAlmostEqual(Material.pure(13).density_kg_per_m3,
                               materials[0].density_kg_per_m3, 4)

    def testmaterials_user_density(self):
        widget = self.wdg.field_formula.widget()
        QtTest.QTest.keyClicks(widget, "Al")

        widget = self.wdg.field_density.suffixWidget()
        self.checkBoxClick(widget)

        widget = self.wdg.field_density.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, "9")

        materials = self.wdg.materials()

        self.assertEqual(1, len(materials))
        self.assertAlmostEqual(9000, materials[0].density_kg_per_m3, 4)

class TestMaterialAdvancedWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = MaterialAdvancedWidget()

    def testmaterials_nomaterials(self):
        materials = self.wdg.materials()

        self.assertEqual(0, len(materials))

    def testmaterials_auto(self):
        self.wdg.tbl_composition.setComposition({13: 1.0})

        materials = self.wdg.materials()

        self.assertEqual(1, len(materials))

        material = materials[0]
        self.assertEqual(generate_name({13: 1.0}), material.name)
        self.assertDictEqual({13: 1.0}, material.composition)
        self.assertAlmostEqual(calculate_density_kg_per_m3({13: 1.0}),
                               material.density_kg_per_m3, 4)

    def testmaterials_user(self):
        widget = self.wdg.field_name.suffixWidget()
        self.checkBoxClick(widget)

        widget = self.wdg.field_name.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, "foo")

        self.wdg.tbl_composition.setComposition({13: 1.0})

        widget = self.wdg.field_density.suffixWidget()
        self.checkBoxClick(widget)

        widget = self.wdg.field_density.widget()
        widget.clear()
        QtTest.QTest.keyClicks(widget, "9")

        materials = self.wdg.materials()

        self.assertEqual(1, len(materials))

        material = materials[0]
        self.assertEqual('foo', material.name)
        self.assertDictEqual({13: 1.0}, material.composition)
        self.assertAlmostEqual(9000, material.density_kg_per_m3, 4)

    def testsetMaterial(self):
        material = Material('foo', {13: 1.0}, 9000)
        self.wdg.setMaterial(material)

        widget = self.wdg.field_name.suffixWidget()
        self.assertFalse(widget.isChecked())

        widget = self.wdg.field_name.widget()
        self.assertEqual(material.name, widget.text())

        widget = self.wdg.field_density.suffixWidget()
        self.assertTrue(widget.isChecked())

        widget = self.wdg.field_density.widget()
        self.assertAlmostEqual(material.density_g_per_cm3, widget.value(), 4)

        composition = self.wdg.tbl_composition.composition()
        self.assertDictEqual(material.composition, composition)

        materials = self.wdg.materials()

        self.assertEqual(1, len(materials))
        self.assertEqual(material, materials[0])

class TestMaterialListWidget(TestCase):

    def setUp(self):
        super().setUp()

        self.wdg = MaterialListWidget()
        self.wdg.setMaterials(self.create_materials())

    def testselectedMaterials(self):
        self.assertEqual(0, len(self.wdg.selectedMaterials()))

    def testselectedMaterials_single(self):
        material = self.wdg.material(0)
        self.wdg.setSelectedMaterials([material])

        selected_materials = self.wdg.selectedMaterials()
        self.assertEqual(1, len(selected_materials))
        self.assertIn(material, selected_materials)

    def testselectedMaterials_remove(self):
        material = self.wdg.material(0)
        self.wdg.setSelectedMaterials([material])

        self.wdg.removeMaterial(material)
        self.assertEqual(2, len(self.wdg.materials()))
        self.assertEqual(0, len(self.wdg.selectedMaterials()))

    def testselectedMaterials_add(self):
        material = self.wdg.material(0)
        self.wdg.setSelectedMaterials([material])

        newmaterial = Material.pure(28)
        self.wdg.addMaterial(newmaterial)
        self.assertIn(newmaterial, self.wdg.materials())

        selected_materials = self.wdg.selectedMaterials()
        self.assertEqual(1, len(selected_materials))
        self.assertIn(material, selected_materials)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
