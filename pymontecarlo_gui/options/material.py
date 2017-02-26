""""""

# Standard library modules.
import functools

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo.options.material import Material
from pymontecarlo.options.composition import \
    generate_name, calculate_density_kg_per_m3, from_formula
from pymontecarlo.program.validator import Validator
from pymontecarlo_gui.options.composition import CompositionTableWidget
from pymontecarlo_gui.widgets.lineedit import ColoredLineEdit
import pymontecarlo_gui.widgets.messagebox as messagebox
from pymontecarlo_gui.widgets.periodictable import PeriodicTableWidget

# Globals and constants variables.
DEFAULT_MATERIAL = Material('Untitled', {}, 0.0)
DEFAULT_VALIDATOR = Validator()

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

class _MaterialWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def materials(self):
        raise NotImplementedError

class MaterialPureWidget(_MaterialWidget):

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

class MaterialFormulaWidget(_MaterialWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.txt_formula = ColoredLineEdit()
        validator = FormulaValidator()
        self.txt_formula.setValidator(validator)
        self.txt_formula.textChanged.emit('')

        self.txt_density = ColoredLineEdit('0')
        validator = QtGui.QDoubleValidator(0.0, float('inf'),
                                           Material.DENSITY_SIGNIFICANT_DIGITS + 3)
        self.txt_density.setValidator(validator)
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
        try:
            formula = self.txt_formula.text()
            composition = from_formula(formula)
            density_kg_per_m3 = calculate_density_kg_per_m3(composition)
        except:
            pass
        else:
            decimals = self.txt_density.validator().decimals()
            fmt = '{{:.{}f}}'.format(decimals)
            text = fmt.format(density_kg_per_m3 / 1e3)
            self.txt_density.setText(text)

    def _on_density_user_changed(self, *args):
        self.txt_density.setEnabled(self.chk_density_user.isChecked())

    def materials(self):
        try:
            formula = self.txt_formula.text()
            density_kg_per_m3 = float(self.txt_density.text()) * 1e3
            return (Material.from_formula(formula, density_kg_per_m3),)
        except:
            return (DEFAULT_MATERIAL,)

class MaterialAdvancedWidget(_MaterialWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.txt_name = ColoredLineEdit()
        self.txt_name.setEnabled(False)
        self.txt_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"^(?!\s*$).+")))

        self.chk_name_auto = QtWidgets.QCheckBox('auto')
        self.chk_name_auto.setChecked(True)

        self.txt_density = ColoredLineEdit('0')
        validator = QtGui.QDoubleValidator(0.0, float('inf'),
                                           Material.DENSITY_SIGNIFICANT_DIGITS + 3)
        self.txt_density.setValidator(validator)
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
                decimals = self.txt_density.validator().decimals()
                fmt = '{{:.{}f}}'.format(decimals)
                text = fmt.format(density_kg_per_m3 / 1e3)
                self.txt_density.setText(text)

    def materials(self):
        try:
            composition = self.tbl_composition.composition()

            if self.chk_name_auto.isChecked():
                name = generate_name(composition)
            else:
                name = self.txt_name.text()

            if self.chk_density_user.isChecked():
                density_kg_per_m3 = float(self.txt_density.text()) * 1e3
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
        self.txt_density.setText(str(material.density_g_per_cm3))

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

    def _init_widget(self):
        raise NotImplementedError

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
        if not index.isValid() or \
                not (0 <= index.row() < len(self._composition)):
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

    def setMaterials(self, materials):
        self._materials.clear()
        self._materials.extend(materials)
        self.modelReset.emit()

    def addMaterial(self, material):
        material = self.validator().validate_material(material, None)
        if material in self._materials:
            return
        self._materials.append(material)
        self.modelReset.emit()

    def updateMaterial(self, row, material):
        self._materials[row] = material
        self.modelReset.emit()

    def removeMaterial(self, material):
        if material not in self._materials:
            return
        self._materials.remove(material)
        self.modelReset.emit()

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

class MaterialListWidget(QtWidgets.QWidget, MaterialValidatorMixin):

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
        self.table.model().updateMaterial(row, materials[0])

    def addMaterial(self, material):
        self.table.model().addMaterial(material)

    def removeMaterial(self, material):
        self.table.model().removeMaterial(material)

    def takeMaterial(self, row):
        model = self.table.model()
        model.removeMaterial(model.data(model.createIndex(row, 0), QtCore.Qt.UserRole))

    def clear(self):
        self.table.model().clearMaterials()

    def materials(self):
        self.table.model().materials()

    def setMaterials(self, materials):
        self.table.model().setMaterials(materials)

    def material(self, row):
        return self.table.model().material(row)

    def setValidator(self, validator):
        super().setValidator(validator)
        self.toolbar.setValidator(validator)
        self.table.model().setValidator(validator)

def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    table = MaterialListWidget()
#
    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__':
    run()
