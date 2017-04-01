""""""

# Standard library modules.
import math
import locale
from collections import OrderedDict

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

import pyxray

# Local modules.
from pymontecarlo.options.composition import to_atomic, process_wildcard
from pymontecarlo.options.material import Material

from pymontecarlo_gui.widgets.label import LabelIcon
from pymontecarlo_gui.widgets.lineedit import ColoredLineEdit
from pymontecarlo_gui.util.tolerance import tolerance_to_decimals

# Globals and constants variables.
MAX_Z = 99

class _ElementComboBox(QtWidgets.QWidget):

    elementChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.combobox = QtWidgets.QComboBox()

        for atomic_number in range(1, MAX_Z + 1):
            text = self._get_item_text(atomic_number)
            self.combobox.addItem(text, atomic_number)

        # Layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combobox)
        self.setLayout(layout)

        # Signal
        self.combobox.currentIndexChanged.connect(self._on_index_changed)

    def _get_item_text(self, atomic_number):
        raise NotImplementedError

    def _on_index_changed(self, index):
        atomic_number = self.combobox.itemData(index)
        self.elementChanged.emit(atomic_number)

    def currentAtomicNumber(self):
        index = self.combobox.currentIndex()
        return self.combobox.itemData(index)

    def setAtomicNumber(self, atomic_number):
        index = self.combobox.findData(atomic_number)
        if index < 0:
            raise ValueError('Unknown atomic number')
        self.combobox.setCurrentIndex(index)

    def availableAtomicNumbers(self):
        atomic_numbers = []
        for row in range(self.combobox.count()):
            atomic_number = self.combobox.itemData(row, QtCore.Qt.UserRole)
            atomic_numbers.append(atomic_number)
        return atomic_numbers

    def setAvailableAtomicNumbers(self, atomic_numbers):
        self.combobox.clear()
        for atomic_number in sorted(atomic_numbers):
            text = self._get_item_text(atomic_number)
            self.combobox.addItem(text, atomic_number)

class ElementSymbolComboBox(_ElementComboBox):

    def _get_item_text(self, atomic_number):
        return pyxray.element_symbol(atomic_number)

class ElementNameComboBox(_ElementComboBox):

    def _get_item_text(self, atomic_number):
        return pyxray.element_name(atomic_number)

class FractionValidator(QtGui.QDoubleValidator):
    """
    :class:`QDoubleValidator` that allows ``?`` as a valid character.
    """

    def __init__(self):
        super().__init__(0.0, 100.0, Material.WEIGHT_FRACTION_SIGNIFICANT_TOLERANCE)

    def validate(self, input, pos):
        if input.strip() == '?':
            return QtGui.QValidator.Acceptable, input, pos
        return super().validate(input, pos)

class CompositionModel(QtCore.QAbstractTableModel):

    def __init__(self, composition=None):
        super().__init__()

        # Variables
        if composition is None:
            composition = {}
        self.setComposition(composition)

    def _update_composition_atomic(self):
        self._composition_atomic = to_atomic(self.composition())

    def rowCount(self, parent=None):
        return len(self._composition) + 1

    def columnCount(self, parent=None):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        tolerance = Material.WEIGHT_FRACTION_SIGNIFICANT_TOLERANCE
        fmt = '{{:.{:d}f}}'.format(max(0, tolerance_to_decimals(tolerance) - 2))

        if row < len(self._composition):
            z = list(self._composition.keys())[row]
            wf = self._composition[z]
            af = self._composition_atomic[z]

            if role == QtCore.Qt.DisplayRole:
                if column == 0:
                    return pyxray.element_symbol(z)
                elif column == 1:
                    if wf == '?':
                        return wf
                    else:
                        return fmt.format(wf * 100.0)
                elif column == 2:
                    return fmt.format(af * 100.0)

            elif role == QtCore.Qt.UserRole:
                if column == 0:
                    return z
                elif column == 1:
                    return wf
                elif column == 2:
                    return af

            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignCenter

        else:
            total_wf = sum(self.composition().values())
            total_af = 1.0 # Always 100%

            if role == QtCore.Qt.DisplayRole:
                if column == 0:
                    return 'Total'
                elif column == 1:
                    return fmt.format(total_wf * 100.0)
                elif column == 2:
                    return fmt.format(total_af * 100.0)

            elif role == QtCore.Qt.UserRole:
                if column == 1:
                    return total_wf
                elif column == 2:
                    return total_af

            elif role == QtCore.Qt.TextAlignmentRole:
                if column == 0:
                    return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
                else:
                    return QtCore.Qt.AlignCenter

            elif role == QtCore.Qt.FontRole:
                font = QtGui.QFont()
                font.setBold(True)
                return font

            elif role == QtCore.Qt.BackgroundRole:
                if not math.isclose(total_wf, 1.0, abs_tol=tolerance):
                    brush = QtGui.QBrush()
                    brush.setColor(QtGui.QColor(255, 192, 203))
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    return brush

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return 'Element'
            elif section == 1:
                return 'Weight fraction (%)'
            elif section == 2:
                return 'Atomic fraction (%)'

        elif orientation == QtCore.Qt.Vertical:
            if section != len(self._composition):
                return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        row = index.row()
        column = index.column()

        if row == len(self._composition):
            return super().flags(index)

        elif column == 2:
            return super().flags(index)

        return QtCore.Qt.ItemFlags(super().flags(index) | QtCore.Qt.ItemIsEditable)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._composition)):
            return False

        row = index.row()
        column = index.column()
        z = list(self._composition.keys())[row]

        if column == 0:
            fraction = self._composition.pop(z)
            self._composition[value] = fraction

        elif column == 1:
            self._composition[z] = value

        self._update_composition_atomic()
        self.dataChanged.emit(index, index)
        return True

    def composition(self):
        return process_wildcard(self._composition)

    def setComposition(self, composition):
        self._composition = \
            OrderedDict(sorted([z, wf] for z, wf in composition.items()))
        self._update_composition_atomic()
        self.modelReset.emit()

    def addElement(self, z=None, fraction=0.0):
        zs = set(self._composition.keys())

        if z is None:
            available_zs = set(range(1, MAX_Z + 1)) - zs
            if not available_zs:
                raise ValueError('No more element can be added')
            z = sorted(available_zs)[0]
        elif z in zs:
            raise ValueError('Element "{0}" already added'
                             .format(pyxray.element_symbol(z)))

        self._composition[z] = fraction

        self._update_composition_atomic()
        self.modelReset.emit()

    def removeElement(self, z):
        if z not in self._composition:
            return
        self._composition.pop(z)
        self._update_composition_atomic()
        self.modelReset.emit()

    def clearElements(self):
        self._composition.clear()
        self._update_composition_atomic()
        self.modelReset.emit()

    def hasElements(self):
        return bool(self._composition)

class CompositionDelegate(QtWidgets.QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        column = index.column()
        if column == 0:
            editor = ElementSymbolComboBox(parent)
            return editor

        elif column == 1:
            editor = ColoredLineEdit(parent)
            editor.setValidator(FractionValidator())
            return editor

        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.UserRole)
        column = index.column()

        if column == 0:
            zs = set(model.composition().keys())
            available_zs = set(range(1, MAX_Z + 1)) - zs
            available_zs.add(value)
            editor.setAvailableAtomicNumbers(available_zs)
            editor.setAtomicNumber(value)

        elif column == 1:
            decimals = tolerance_to_decimals(Material.WEIGHT_FRACTION_SIGNIFICANT_TOLERANCE) - 2
            fmt = '{{:.{}f}}'.format(decimals)
            if value == '?':
                editor.setText(value)
            else:
                editor.setText(fmt.format(value * 100.0))

        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        column = index.column()
        if column == 0:
            model.setData(index, editor.currentAtomicNumber())
        elif column == 1:
            text = editor.text().strip()
            if text != '?':
                text = locale.atof(editor.text()) / 100.0
            model.setData(index, text)
        else:
            return super().setModelData(editor, model, index)

class CompositionToolBar(QtWidgets.QToolBar):

    def __init__(self, table, parent=None):
        super().__init__(parent)

        # Variables
        self.table = table

        # Actions
        self.act_add = self.addAction(QtGui.QIcon.fromTheme("list-add"), "Add")

        self.act_remove = self.addAction(QtGui.QIcon.fromTheme("list-remove"), "Remove")
        self.act_remove.setEnabled(False)
        self.act_remove.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.act_remove.setShortcut(QtGui.QKeySequence.Delete)

        self.act_clear = self.addAction(QtGui.QIcon.fromTheme("edit-clear"), "Clear")
        self.act_clear.setEnabled(False)

        # Signals
        self.table.model().modelReset.connect(self._on_data_changed)
        self.table.selectionModel().selectionChanged.connect(self._on_data_changed)
#
        self.act_add.triggered.connect(self._on_add_element)
        self.act_remove.triggered.connect(self._on_remove_element)
        self.act_clear.triggered.connect(self._on_clear_elements)

    def _on_data_changed(self):
        model = self.table.model()
        has_rows = model.hasElements()

        selection_model = self.table.selectionModel()
        has_selection = selection_model.hasSelection()

        self.act_remove.setEnabled(has_rows and has_selection)
        self.act_clear.setEnabled(has_rows)

    def _on_add_element(self):
        self.table.model().addElement()

    def _on_remove_element(self):
        selection_model = self.table.selectionModel()
        if not selection_model.hasSelection():
            return

        indexes = selection_model.selectedIndexes()
        model = self.table.model()
        for row in reversed([index.row() for index in indexes]):
            model.removeElement(model.data(model.createIndex(row, 0), QtCore.Qt.UserRole))

    def _on_clear_elements(self):
        model = self.table.model()
        model.clearElements()

class CompositionTableWidget(QtWidgets.QWidget):

    compositionChanged = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        model = CompositionModel()
        delegate = CompositionDelegate()

        # Widgets
        self.table = QtWidgets.QTableView()
        self.table.setModel(model)
        self.table.setItemDelegate(delegate)

        header = self.table.horizontalHeader()
        for column in range(self.table.model().columnCount()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)

        self.toolbar = CompositionToolBar(self.table)

        self.lbl_info = LabelIcon('Use "?" to balance composition',
                                  QtGui.QIcon.fromTheme("dialog-information"))
        self.lbl_info.setVerticalAlignment(QtCore.Qt.AlignCenter)

        # Layouts
        lyt_bottom = QtWidgets.QHBoxLayout()
        lyt_bottom.addWidget(self.lbl_info)
        lyt_bottom.addStretch()
        lyt_bottom.addWidget(self.toolbar)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(lyt_bottom)
        self.setLayout(layout)

        # Signals
        model.dataChanged.connect(self._on_changed)
        model.modelReset.connect(self._on_changed)

    def _on_changed(self, *args, **kwargs):
        self.compositionChanged.emit(self.composition())

    def composition(self):
        return self.table.model().composition()

    def setComposition(self, composition):
        self.table.model().setComposition(composition)

def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    composition = {5: 0.2, 14: 0.5, 29: 0.3}

    table = CompositionTableWidget()
    table.setComposition(composition)
#
    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(table)
    mainwindow.show()

#    table.model().addElement(3, 0.6)
#    table.model().removeElement(14)

    app.exec_()

if __name__ == '__main__':
    run()
