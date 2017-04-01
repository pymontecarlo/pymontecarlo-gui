""""""

# Standard library modules.
import math
import abc
import operator
import locale

# Third party modules.
from qtpy import QtWidgets, QtCore, QtGui

import numpy as np

# Local modules.
from pymontecarlo.options.sample.base import Sample, Layer

from pymontecarlo_gui.widgets.field import LabelField, GroupField
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.widgets.label import LabelIcon
from pymontecarlo_gui.util.tolerance import tolerance_to_decimals
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.util.validate import Validable, INVALID_COLOR
from pymontecarlo_gui.options.material import MaterialListWidget

# Globals and constants variables.

#--- Fields

class TiltField(LabelField):

    tiltsChanged = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Tilt(s) [\u00b0]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(Sample.TILT_TOLERANCE_rad))
        self._widget.setRange(-180.0, 180.0, decimals)
        self._widget.setValues([0.0])

        # Signals
        self._widget.valuesChanged.connect(self.tiltsChanged)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def tilts_deg(self):
        return self._widget.values()

    def setTilts_deg(self, tilts_deg):
        self._widget.setValues(tilts_deg)

class RotationField(LabelField):

    rotationsChanged = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Rotation(s) [\u00b0]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(Sample.ROTATION_TOLERANCE_rad))
        self._widget.setRange(0.0, 360.0, decimals)
        self._widget.setValues([0.0])

        # Signals
        self._widget.valuesChanged.connect(self.rotationsChanged)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def rotations_deg(self):
        return self._widget.values()

    def setRotations_deg(self, rotations_deg):
        self._widget.setValues(rotations_deg)

class MaterialField(GroupField):

    materialsChanged = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = MaterialListWidget()

        # Signals
        self._widget.selectionChanged.connect(self.materialsChanged)

    def _create_group_box(self):
        groupbox = super()._create_group_box()
        groupbox.setStyleSheet('color: blue')
        return groupbox

    def title(self):
        return 'Material(s)'

    def widget(self):
        return self._widget

    def materials(self):
        return self._widget.selectedMaterials()

    def setMaterials(self, materials):
        self._widget.setSelectedMaterials(materials)

    def availableMaterials(self):
        return self._widget.materials()

    def setAvailableMaterials(self, materials):
        self._widget.setMaterials(materials)

class DiameterField(LabelField):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Diameter(s) [nm]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        tolerance = self._get_tolerance_m()
        decimals = tolerance_to_decimals(tolerance)
        self._widget.setRange(tolerance, float('inf'), decimals)
        self._widget.setValues([100.0])

    @abc.abstractmethod
    def _get_tolerance_m(self):
        raise NotImplementedError

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def diameters_m(self):
        return np.array(self._widget.values()) * 1e-9

    def setDiameters_m(self, diameters_m):
        values = np.array(diameters_m) * 1e9
        self._widget.setValues(values)

#--- Layers

class LayerRow:

    def __init__(self):
        self.materials = []
        self.thicknesses_m = []

    def isValid(self):
        return bool(self.materials) and bool(self.thicknesses_m)

class LayerRowModel(QtCore.QAbstractTableModel, Validable):

    MIMETYPE = 'application/layerrow'

    def __init__(self):
        super().__init__()

        self._layerrows = []

        tolerance = Layer.THICKNESS_TOLERANCE_m * 1e9
        decimals = tolerance_to_decimals(tolerance)
        self.thickness_format = '%.{}f'.format(decimals)

    def rowCount(self, *args, **kwargs):
        return len(self._layerrows)

    def columnCount(self, *args, **kwargs):
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._layerrows)):
            return None

        row = index.row()
        column = index.column()
        layerrow = self._layerrows[row]

        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                if not layerrow.materials:
                    return 'none'
                else:
                    return ', '.join(map(operator.attrgetter('name'), layerrow.materials))
            elif column == 1:
                if len(layerrow.thicknesses_m) > 0:
                    values = np.array(layerrow.thicknesses_m) * 1e9
                    return ', '.join(locale.format(self.thickness_format, v) for v in values)

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        elif role == QtCore.Qt.UserRole:
            return layerrow

        elif role == QtCore.Qt.BackgroundRole:
            if not layerrow.isValid():
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(INVALID_COLOR))
                brush.setStyle(QtCore.Qt.SolidPattern)
                return brush

    def headerData(self, section , orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return 'Material(s)'
                elif section == 1:
                    return 'Thickness(es) [nm]'

            elif orientation == QtCore.Qt.Vertical:
                return str(section + 1)

    def flags(self, index):
        flags = super().flags(index)

        if index.isValid():
            return flags | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        else:
            return flags | QtCore.Qt.ItemIsDropEnabled

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role != QtCore.Qt.EditRole:
            return False

        row = index.row()
        self._layerrows[row] = value

        self.dataChanged.emit(index, index)
        return True

    def supportedDragActions(self):
        return QtCore.Qt.MoveAction

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def mimeTypes(self):
        mimetypes = super().mimeTypes()
        mimetypes.append(self.MIMETYPE)
        return mimetypes

    def mimeData(self, indexes):
        rows = list(set(index.row() for index in indexes))

        if len(rows) != 1:
            return QtCore.QMimeData()

        mimedata = QtCore.QMimeData()
        mimedata.setData(self.MIMETYPE, str(rows[0]).encode('ascii'))

        return mimedata

    def canDropMimeData(self, mimedata, action, row, column, parent):
        if not mimedata.hasFormat(self.MIMETYPE):
            return False

        if action != QtCore.Qt.MoveAction:
            return False

        return True

    def dropMimeData(self, mimedata, action, row, column, parent):
        if not self.canDropMimeData(mimedata, action, row, column, parent):
            return False

        if action == QtCore.Qt.IgnoreAction:
            return True

        if row != -1:
            newrow = row
        elif parent.isValid():
            newrow = parent.row()
        else:
            newrow = self.rowCount()

        oldrow = int(mimedata.data(self.MIMETYPE).data().decode('ascii'))

        layerrow = self._layerrows.pop(oldrow)
        self._layerrows.insert(newrow, layerrow)

        self.modelReset.emit()

        return True

    def isValid(self):
        return super().isValid() and all(r.isValid() for r in self._layerrows)

    def _add_layerrow(self, layerrow):
        self._layerrows.append(layerrow)

    def addLayerRow(self, layerrow):
        self._add_layerrow(layerrow)
        self.modelReset.emit()

    def addNewLayerRow(self):
        self.addLayerRow(LayerRow())

    def updateLayerRow(self, row, layerrow):
        self._layerrows[row] = layerrow
        self.modelReset.emit()

    def removeLayerRow(self, layerrow):
        if layerrow not in self._layerrows:
            return
        self._layerrows.remove(layerrow)
        self.modelReset.emit()

    def clearLayerRows(self):
        self._layerrows.clear()
        self.modelReset.emit()

    def hasLayerRows(self):
        return bool(self._layerrows)

    def layerRow(self, row):
        return self._layerrows[row]

    def layerRows(self):
        return tuple(self._layerrows)

    def setLayerRows(self, layerrows):
        self.clearMaterials()
        for layerrow in layerrows:
            self._add_layerrow(layerrow)
        self.modelReset.emit()

class LayerRowDelegate(QtWidgets.QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._available_materials = []

    def createEditor(self, parent, option, index):
        column = index.column()
        if column == 0:
            editor = MaterialListWidget(parent)

            editor.setMaximumHeight(parent.height())
            editor.setMinimumSize(editor.sizeHint())

            return editor

        elif column == 1:
            editor = ColoredMultiFloatLineEdit(parent)

            tolerance = Layer.THICKNESS_TOLERANCE_m * 1e9
            decimals = tolerance_to_decimals(tolerance)
            editor.setRange(tolerance, float('inf'), decimals)

            return editor

    def setEditorData(self, editor, index):
        model = index.model()
        layerrow = model.data(index, QtCore.Qt.UserRole)
        column = index.column()

        if column == 0:
            editor.setMaterials(self._available_materials)
            editor.setSelectedMaterials(layerrow.materials)
            editor.setAllowVacuum(True)

        elif column == 1:
            values = np.array(layerrow.thicknesses_m) * 1e9
            editor.setValues(values)

    def setModelData(self, editor, model, index):
        column = index.column()
        layerrow = model.data(index, QtCore.Qt.UserRole)

        if column == 0:
            layerrow.materials = editor.selectedMaterials()

        elif column == 1:
            values = editor.values()
            layerrow.thicknesses_m = np.array(values) * 1e-9

        model.updateLayerRow(index.row(), layerrow)

    def availableMaterials(self):
        return self._available_materials

    def setAvailableMaterials(self, materials):
        self._available_materials.clear()
        self._available_materials.extend(materials)

class LayerRowToolbar(QtWidgets.QToolBar):

    def __init__(self, table, parent=None):
        super().__init__(parent)

        # Variables
        self.table = table

        # Actions
        self.act_add = self.addAction(QtGui.QIcon.fromTheme("list-add"), "Pure")
        self.act_add.setToolTip('Add layer')

        self.act_remove = self.addAction(QtGui.QIcon.fromTheme("list-remove"), 'Remove')
        self.act_remove.setToolTip('Remove')
        self.act_remove.setEnabled(False)
        self.act_remove.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.act_remove.setShortcut(QtGui.QKeySequence.Delete)

        self.act_clear = self.addAction(QtGui.QIcon.fromTheme("edit-clear"), 'Clear')
        self.act_clear.setToolTip('Clear')
        self.act_clear.setEnabled(False)

        # Signals
        self.table.model().modelReset.connect(self._on_data_changed)
        self.table.selectionModel().selectionChanged.connect(self._on_data_changed)

        self.act_add.triggered.connect(self._on_add_layer)
        self.act_remove.triggered.connect(self._on_remove_layer)
        self.act_clear.triggered.connect(self._on_clear_layers)

    def _on_data_changed(self):
        model = self.table.model()
        has_rows = model.hasLayerRows()

        selection_model = self.table.selectionModel()
        has_selection = selection_model.hasSelection()

        self.act_remove.setEnabled(has_rows and has_selection)
        self.act_clear.setEnabled(has_rows)

    def _on_add_layer(self):
        model = self.table.model()
        model.addNewLayerRow()

    def _on_remove_layer(self):
        selection_model = self.table.selectionModel()
        if not selection_model.hasSelection():
            return

        indexes = selection_model.selectedIndexes()
        model = self.table.model()
        for row in reversed([index.row() for index in indexes]):
            model.removeLayerRow(model.data(model.createIndex(row, 0), QtCore.Qt.UserRole))

    def _on_clear_layers(self):
        model = self.table.model()
        model.clearLayerRows()

class LayersWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Variables
        model = LayerRowModel()

        # Widgets
        self.table = QtWidgets.QTableView()
        self.table.setModel(model)
        self.table.setItemDelegate(LayerRowDelegate())
        self.table.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setDragDropMode(QtWidgets.QTableView.InternalMove)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)

        header = self.table.horizontalHeader()
        for column in range(self.table.model().columnCount()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)

        header.setStyleSheet('color: blue')

        self.toolbar = LayerRowToolbar(self.table)

        self.lbl_info = LabelIcon('Double-click to modify\nDrag and drop to move layer',
                                  QtGui.QIcon.fromTheme("dialog-information"))
        self.lbl_info.setVerticalAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

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

    def availableMaterials(self):
        return self.table.itemDelegate().availableMaterials()

    def setAvailableMaterials(self, materials):
        self.table.itemDelegate().setAvailableMaterials(materials)

    def layersList(self):
        return []

#--- Base widgets

class SampleWidget(QtWidgets.QWidget, Validable, metaclass=QABCMeta):

    def __init__(self, parent=None):
        super().__init__(parent)

    def isValid(self):
        return super().isValid() and bool(self.samples())

    @abc.abstractmethod
    def samples(self):
        """
        Returns a :class:`list` of :class:`Sample`.
        """
        return []

    @abc.abstractmethod
    def setAvailableMaterials(self, materials):
        raise NotImplementedError

def run_layerswidget(): #pragma: no cover
    import sys
    app = QtWidgets.QApplication(sys.argv)

    from pymontecarlo.options.material import Material

    materials = []
    for z in range(14, 79, 5):
        materials.append(Material.pure(z))

    widget = LayersWidget()
    widget.setAvailableMaterials(materials)

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run_layerswidget()
