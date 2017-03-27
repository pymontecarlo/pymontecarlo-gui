""""""

# Standard library modules.
import functools

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo.options.material import Material, VACUUM
from pymontecarlo.options.composition import \
    generate_name, calculate_density_kg_per_m3, from_formula
from pymontecarlo.program.validator import Validator
from pymontecarlo_gui.options.composition import CompositionTableWidget
from pymontecarlo_gui.widgets.lineedit import \
    ColoredLineEdit, ColoredFloatLineEdit
import pymontecarlo_gui.widgets.messagebox as messagebox
from pymontecarlo_gui.widgets.periodictable import PeriodicTableWidget

# Globals and constants variables.
DEFAULT_MATERIAL = Material('Untitled', {}, 0.0)
DEFAULT_VALIDATOR = Validator()

#--- Mix-ins

class MaterialValidatorMixin:

    def validator(self):
        if not hasattr(self, '_validator'):
            self._validator = DEFAULT_VALIDATOR
        return self._validator

    def setValidator(self, validator):
        """
        Sets pyMonteCarlo's validator.
        """
        assert hasattr(validator, 'validate_material')
        self._validator = validator

class MaterialAbstractViewMixin(MaterialValidatorMixin):

    def _model(self):
        raise NotImplementedError

    def addMaterial(self, material):
        self._model().addMaterial(material)

    def removeMaterial(self, material):
        self._model().removeMaterial(material)

    def takeMaterial(self, row):
        model = self._model()
        model.removeMaterial(model.data(model.createIndex(row, 0), QtCore.Qt.UserRole))

    def clear(self):
        self._model().clearMaterials()

    def materials(self):
        return self._model().materials()

    def setMaterials(self, materials):
        self._model().setMaterials(materials)

    def material(self, row):
        return self._model().material(row)

    def setValidator(self, validator):
        super().setValidator(validator)
        self._model().setValidator(validator)

class MaterialVacuumMixin:

    def allowVacuum(self):
        return VACUUM in self.materials()

    def setAllowVacuum(self, allow):
        if allow:
            self.addMaterial(VACUUM)
        else:
            self.removeMaterial(VACUUM)

#--- Validators

class FormulaValidator(QtGui.QRegExpValidator):

    def __init__(self):
        super().__init__(QtCore.QRegExp(r'^[\w ]+$'))

    def validate(self, input, pos):
        out, input, pos = super().validate(input, pos)
        if out == QtGui.QValidator.Invalid:
            return QtGui.QValidator.Invalid, input, pos

        try:
            from_formula(input)
        except:
            return QtGui.QValidator.Intermediate, input, pos

        return QtGui.QValidator.Acceptable, input, pos

#--- Widgets

class MaterialWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def materials(self):
        raise NotImplementedError

class MaterialPureWidget(MaterialWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_periodic_table = PeriodicTableWidget()
        self.wdg_periodic_table.setMultipleSelection(True)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.wdg_periodic_table)
        self.setLayout(layout)

    def materials(self):
        materials = []
        for z in self.wdg_periodic_table.selection():
            materials.append(Material.pure(z))
        return tuple(materials)

class MaterialFormulaWidget(MaterialWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.txt_formula = ColoredLineEdit()
        validator = FormulaValidator()
        self.txt_formula.setValidator(validator)
        self.txt_formula.textChanged.emit('')

        self.txt_density = ColoredFloatLineEdit()
        self.txt_density.setRange(0.0, float('inf'))
        self.txt_density.setDecimals(Material.DENSITY_SIGNIFICANT_TOLERANCE_kg_per_m3 + 3)
        self.txt_density.setValue(0.0)
        self.txt_density.setEnabled(False)

        self.chk_density_user = QtWidgets.QCheckBox('user defined')
        self.chk_density_user.setChecked(False)

        # Layouts
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel("Formula"), 0, 0)
        layout.addWidget(self.txt_formula, 0, 1)
        layout.addWidget(QtWidgets.QLabel("Density (g/cm<sup>3</sup>)"), 1, 0)
        layout.addWidget(self.txt_density, 1, 1)
        layout.addWidget(self.chk_density_user, 1, 2)
        self.setLayout(layout)

        # Signals
        self.txt_formula.textChanged.connect(self._on_formula_changed)
        self.chk_density_user.stateChanged.connect(self._on_density_user_changed)

    def _on_formula_changed(self, *args):
        if self.chk_density_user.isChecked():
            return

        try:
            formula = self.txt_formula.text()
            composition = from_formula(formula)
            density_kg_per_m3 = calculate_density_kg_per_m3(composition)
        except:
            pass
        else:
            self.txt_density.setValue(density_kg_per_m3 / 1e3)

    def _on_density_user_changed(self, *args):
        self.txt_density.setEnabled(self.chk_density_user.isChecked())

    def materials(self):
        try:
            formula = self.txt_formula.text()

            if self.chk_density_user.isChecked():
                density_kg_per_m3 = self.txt_density.value() * 1e3
            else:
                composition = from_formula(formula)
                density_kg_per_m3 = calculate_density_kg_per_m3(composition)

            return (Material.from_formula(formula, density_kg_per_m3),)
        except:
            return (DEFAULT_MATERIAL,)

class MaterialAdvancedWidget(MaterialWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.txt_name = ColoredLineEdit()
        self.txt_name.setEnabled(False)
        self.txt_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"^(?!\s*$).+")))

        self.chk_name_auto = QtWidgets.QCheckBox('auto')
        self.chk_name_auto.setChecked(True)

        self.txt_density = ColoredFloatLineEdit()
        self.txt_density.setRange(0.0, float('inf'))
        self.txt_density.setDecimals(Material.DENSITY_SIGNIFICANT_TOLERANCE_kg_per_m3 + 3)
        self.txt_density.setValue(0.0)
        self.txt_density.setEnabled(False)

        self.chk_density_user = QtWidgets.QCheckBox('user defined')
        self.chk_density_user.setChecked(False)

        self.tbl_composition = CompositionTableWidget()

        # Layouts
        lyt_top = QtWidgets.QGridLayout()
        lyt_top.addWidget(QtWidgets.QLabel("Name"), 0, 0)
        lyt_top.addWidget(self.txt_name, 0, 1)
        lyt_top.addWidget(self.chk_name_auto, 0, 2)
        lyt_top.addWidget(QtWidgets.QLabel("Density (g/cm<sup>3</sup>)"), 1, 0)
        lyt_top.addWidget(self.txt_density, 1, 1)
        lyt_top.addWidget(self.chk_density_user, 1, 2)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(lyt_top)
        layout.addWidget(self.tbl_composition)
        self.setLayout(layout)

        # Signals
        self.chk_name_auto.stateChanged.connect(self._on_name_auto_changed)
        self.chk_density_user.stateChanged.connect(self._on_density_user_changed)
        self.tbl_composition.compositionChanged.connect(self._on_composition_changed)

    def _on_name_auto_changed(self, *args):
        self.txt_name.setEnabled(not self.chk_name_auto.isChecked())

    def _on_density_user_changed(self, *args):
        self.txt_density.setEnabled(self.chk_density_user.isChecked())

    def _on_composition_changed(self, composition):
        if self.chk_name_auto.isChecked():
            try:
                name = generate_name(composition)
            except:
                pass
            else:
                self.txt_name.setText(name)

        if not self.chk_density_user.isChecked():
            try:
                density_kg_per_m3 = calculate_density_kg_per_m3(composition)
            except:
                pass
            else:
                self.txt_density.setValue(density_kg_per_m3 / 1e3)

    def materials(self):
        try:
            composition = self.tbl_composition.composition()

            if self.chk_name_auto.isChecked():
                name = generate_name(composition)
            else:
                name = self.txt_name.text()

            if self.chk_density_user.isChecked():
                density_kg_per_m3 = self.txt_density.value() * 1e3
            else:
                density_kg_per_m3 = calculate_density_kg_per_m3(composition)

            return (Material(name, composition, density_kg_per_m3),)
        except:
            return (DEFAULT_MATERIAL,)

    def setMaterial(self, material):
        self.chk_name_auto.setChecked(False)
        self.txt_name.setText(material.name)
        self.tbl_composition.setComposition(material.composition)
        self.chk_density_user.setChecked(True)
        self.txt_density.setValue(material.density_g_per_cm3)

class MaterialDialog(QtWidgets.QDialog, MaterialValidatorMixin):

    def __init__(self, material_widget_class, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Material')

        # Variables
        self._materials = []

        # Widgets
        self.wdg_material = material_widget_class()

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | \
                                             QtWidgets.QDialogButtonBox.Cancel)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.wdg_material)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # Signals
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self._on_cancel)

    def _on_ok(self):
        try:
            self._materials.clear()
            for material in self.wdg_material.materials():
                material = self.validator().validate_material(material, None)
                self._materials.append(material)
        except Exception as ex:
            messagebox.exception(self, ex)
            return

        self.accept()

    def _on_cancel(self):
        self._materials.clear()
        self.reject()

    def materials(self):
        return self._materials

class MaterialModel(QtCore.QAbstractListModel, MaterialValidatorMixin):

    def __init__(self):
        super().__init__()

        # Variables
        self._materials = []

    def rowCount(self, parent=None):
        return len(self._materials)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        material = self._materials[row]

        if role == QtCore.Qt.DisplayRole:
            return material.name

        elif role == QtCore.Qt.UserRole:
            return material

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role != QtCore.Qt.EditRole:
            return False

        try:
            self.validator().validate_material(value, None)
        except:
            return False

        row = index.row()
        self._materials[row] = value

        self.dataChanged.emit(index, index)
        return True

    def materials(self):
        return tuple(self._materials)

    def _addMaterial(self, material):
        material = self.validator().validate_material(material, None)
        if material in self._materials:
            return False
        self._materials.append(material)
        return True

    def setMaterials(self, materials):
        self._materials.clear()
        for material in materials:
            self._addMaterial(material)
        self.modelReset.emit()

    def addMaterial(self, material):
        added = self._addMaterial(material)
        if added:
            self.modelReset.emit()
        return added

    def updateMaterial(self, row, material):
        self._materials[row] = material
        self.modelReset.emit()

    def removeMaterial(self, material):
        if material not in self._materials:
            return False
        self._materials.remove(material)
        self.modelReset.emit()
        return False

    def clearMaterials(self):
        self._materials.clear()
        self.modelReset.emit()

    def hasMaterials(self):
        return bool(self._materials)

    def material(self, row):
        return self._materials[row]

class MaterialToolbar(QtWidgets.QToolBar, MaterialValidatorMixin):

    def __init__(self, table, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        # Variables
        self.table = table

        # Actions
        self.act_add_pure = self.addAction(QtGui.QIcon.fromTheme("list-add"), "Pure")
        self.act_add_pure.setToolTip('Add pure material')

        self.act_add_formula = self.addAction(QtGui.QIcon.fromTheme("list-add"), "Formula")
        self.act_add_pure.setToolTip('Add material from a formula')

        self.act_add_material = self.addAction(QtGui.QIcon.fromTheme("list-add"), "Advanced")
        self.act_add_pure.setToolTip('Add material from composition')

        self.act_remove = QtWidgets.QAction()
        self.act_remove.setIcon(QtGui.QIcon.fromTheme("list-remove"))
        self.act_remove.setToolTip('Remove')
        self.act_remove.setEnabled(False)
        self.act_remove.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.act_remove.setShortcut(QtGui.QKeySequence.Delete)

        self.act_clear = QtWidgets.QAction()
        self.act_clear.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        self.act_clear.setToolTip('Clear')
        self.act_clear.setEnabled(False)

        # Widgets
        tool_remove = QtWidgets.QToolButton()
        tool_remove.setDefaultAction(self.act_remove)
        self.addWidget(tool_remove)

        tool_clear = QtWidgets.QToolButton()
        tool_clear.setDefaultAction(self.act_clear)
        self.addWidget(tool_clear)

        # Signals
        self.table.model().modelReset.connect(self._on_data_changed)
        self.table.selectionModel().selectionChanged.connect(self._on_data_changed)

        self.act_add_pure.triggered.connect(functools.partial(self._on_add_material, MaterialPureWidget))
        self.act_add_formula.triggered.connect(functools.partial(self._on_add_material, MaterialFormulaWidget))
        self.act_add_material.triggered.connect(functools.partial(self._on_add_material, MaterialAdvancedWidget))
        self.act_remove.triggered.connect(self._on_remove_material)
        self.act_clear.triggered.connect(self._on_clear_materials)

    def _on_data_changed(self):
        model = self.table.model()
        has_rows = model.hasMaterials()

        selection_model = self.table.selectionModel()
        has_selection = selection_model.hasSelection()

        self.act_remove.setEnabled(has_rows and has_selection)
        self.act_clear.setEnabled(has_rows)

    def _on_add_material(self, material_widget_class):
        dialog = MaterialDialog(material_widget_class)
        dialog.setWindowTitle('Add material')
        dialog.setValidator(self.validator())

        if not dialog.exec_():
            return

        for material in dialog.materials():
            self.table.model().addMaterial(material)

    def _on_remove_material(self):
        selection_model = self.table.selectionModel()
        if not selection_model.hasSelection():
            return

        indexes = selection_model.selectedIndexes()
        model = self.table.model()
        for row in reversed([index.row() for index in indexes]):
            model.removeMaterial(model.data(model.createIndex(row, 0), QtCore.Qt.UserRole))

    def _on_clear_materials(self):
        model = self.table.model()
        model.clearMaterials()

class MaterialsWidget(QtWidgets.QWidget, MaterialAbstractViewMixin):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        model = MaterialModel()

        # Widgets
        self.table = QtWidgets.QListView()
        self.table.setModel(model)

        self.toolbar = MaterialToolbar(self.table)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addWidget(self.toolbar, 0, QtCore.Qt.AlignRight)
        self.setLayout(layout)

        # Signals
        self.table.doubleClicked.connect(self._on_double_clicked)

    def _model(self):
        return self.table.model()

    def _on_double_clicked(self, index):
        row = index.row()
        material = self.material(row)

        dialog = MaterialDialog(MaterialAdvancedWidget)
        dialog.setWindowTitle('Edit material')
        dialog.setValidator(self.validator())
        dialog.wdg_material.setMaterial(material)

        if not dialog.exec_():
            return

        materials = dialog.materials()
        if not materials:
            return

        assert len(materials) == 1
        self._model().updateMaterial(row, materials[0])

    def setValidator(self, validator):
        super().setValidator(validator)
        self.toolbar.setValidator(validator)

class MaterialComboBox(QtWidgets.QWidget, MaterialAbstractViewMixin, MaterialVacuumMixin):

    currentMaterialChanged = QtCore.Signal(Material)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        model = MaterialModel()

        # Widgets
        self.combobox = QtWidgets.QComboBox()
        self.combobox.setModel(model)
        self.combobox.setEditable(False)
        self.combobox.setCurrentIndex(0)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combobox)
        self.setLayout(layout)

        # Signals
        model.modelReset.connect(self._on_model_reset)
        self.combobox.currentIndexChanged.connect(self._on_current_index_changed)

    def _model(self):
        return self.combobox.model()

    def _on_model_reset(self, *args):
        if self.combobox.currentIndex() < 0:
            self.combobox.setCurrentIndex(0)

    def _on_current_index_changed(self, index):
        self.currentMaterialChanged.emit(self.currentMaterial())

    def currentMaterial(self):
        row = self.combobox.currentIndex()
        return self._model().material(row)

    def setCurrentMaterial(self, material):
        materials = self.materials()
        try:
            row = materials.index(material)
        except ValueError:
            row = -1
        self.combobox.setCurrentIndex(row)

class CheckableMaterialModel(MaterialModel):

    def __init__(self):
        super().__init__()

        self._selection = []

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == QtCore.Qt.CheckStateRole:
            row = index.row()
            return QtCore.Qt.Checked if self._selection[row] else QtCore.Qt.Unchecked

        return super().data(index, role)

    def flags(self, index):
        return super().flags(index) | QtCore.Qt.ItemIsUserCheckable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role == QtCore.Qt.CheckStateRole:
            row = index.row()
            self._selection[row] = value == QtCore.Qt.Checked

            self.dataChanged.emit(index, index)
            return True

        return super().setData(index, value, role=role)

    def _addMaterial(self, material):
        if not super()._addMaterial(material):
            return False
        self._selection.append(False)
        return True

    def removeMaterial(self, material):
        try:
            row = self._materials.index(material)
        except IndexError:
            return False

        if not super().removeMaterial(material):
            return False

        self._selection.pop(row)
        return True

    def clearMaterials(self):
        super().clearMaterials()
        self._selection.clear()

    def selectedMaterials(self):
        return tuple(m for m, s in zip(self._materials, self._selection) if s)

    def setSelectedMaterials(self, materials):
        for row in range(len(self._selection)):
            self._selection[row] = False

        for material in materials:
            try:
                row = self._materials.index(material)
            except IndexError:
                continue
            self._selection[row] = True

class MaterialListWidget(QtWidgets.QWidget, MaterialAbstractViewMixin, MaterialVacuumMixin):

    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        model = CheckableMaterialModel()

        # Widgets
        self.listview = QtWidgets.QListView()
        self.listview.setModel(model)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.listview)
        self.setLayout(layout)

        # Signals
        model.dataChanged.connect(self.selectionChanged)

    def _model(self):
        return self.listview.model()

    def selectedMaterials(self):
        return self._model().selectedMaterials()

    def setSelectedMaterials(self, materials):
        self._model().setSelectedMaterials(materials)

def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    table = MaterialsWidget()

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

    app.exec_()

def run2():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    material = Material.pure(14)

    widget = MaterialComboBox()
    widget.addMaterial(material)
    widget.addMaterial(Material.pure(14))
    widget.addMaterial(Material.pure(13))
    widget.addMaterial(Material.pure(10))
    widget.setAllowVacuum(False)
    widget.setCurrentMaterial(material)

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

def run3():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    material = Material.pure(14)

    widget = MaterialListWidget()
    widget.addMaterial(material)
    widget.addMaterial(Material.pure(14))
    widget.addMaterial(Material.pure(13))
    widget.addMaterial(Material.pure(10))
    widget.setAllowVacuum(True)
    #widget.setCurrentMaterial(material)

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    print(widget.selectedMaterials())

    app.exec_()

if __name__ == '__main__':
    run3()
