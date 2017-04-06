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
from pymontecarlo.options.sample.base import Sample, Layer, LayerBuilder

from pymontecarlo_gui.widgets.field import Field
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.widgets.label import LabelIcon
from pymontecarlo_gui.util.tolerance import tolerance_to_decimals
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.util.validate import Validable, INVALID_COLOR
from pymontecarlo_gui.options.material import MaterialListWidget

# Globals and constants variables.

#--- Fields

class TiltField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Tilts [\u00b0]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        decimals = tolerance_to_decimals(math.degrees(Sample.TILT_TOLERANCE_rad))
        self._widget.setRange(-180.0, 180.0, decimals)
        self._widget.setValues([0.0])

        # Signals
        self._widget.valuesChanged.connect(self.changed)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def tilts_deg(self):
        return self._widget.values()

    def setTilts_deg(self, tilts_deg):
        self._widget.setValues(tilts_deg)

class RotationField(Field):

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
        self._widget.valuesChanged.connect(self.changed)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def rotations_deg(self):
        return self._widget.values()

    def setRotations_deg(self, rotations_deg):
        self._widget.setValues(rotations_deg)

class MaterialField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Material(s)')

        self._widget = MaterialListWidget()

        # Signals
        self._widget.selectionChanged.connect(self.changed)

    def label(self):
        return self._label

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

class DiameterField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Diameter(s) [nm]')
        self._label.setStyleSheet('color: blue')

        self._widget = ColoredMultiFloatLineEdit()
        tolerance = self._get_tolerance_m() * 1e9
        decimals = tolerance_to_decimals(tolerance)
        self._widget.setRange(tolerance, float('inf'), decimals)
        self._widget.setValues([100.0])

        # Widgets
        self._widget.valuesChanged.connect(self.changed)

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

class LayerBuilderField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Layers')

        self._widget = LayerBuilderWidget()

        # Signals
        self._widget.layerBuildersChanged.connect(self.changed)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def layerBuilders(self):
        return self._widget.layerBuilders()

    def setLayerBuilders(self, builders):
        self._widget.setLayerBuilders(builders)

    def availableMaterials(self):
        return self._widget.availableMaterials()

    def setAvailableMaterials(self, materials):
        self._widget.setAvailableMaterials(materials)

#--- Layers

class LayerBuilderModel(QtCore.QAbstractTableModel, Validable):

    MIMETYPE = 'pymontecarlo/layerbuilder'

    def __init__(self):
        super().__init__()

        self._builders = []

        tolerance = Layer.THICKNESS_TOLERANCE_m * 1e9
        decimals = tolerance_to_decimals(tolerance)
        self.thickness_format = '%.{}f'.format(decimals)

    def rowCount(self, *args, **kwargs):
        return len(self._builders)

    def columnCount(self, *args, **kwargs):
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._builders)):
            return None

        row = index.row()
        column = index.column()
        builder = self._builders[row]

        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                if not builder.materials:
                    return 'none'
                else:
                    return ', '.join(map(operator.attrgetter('name'), builder.materials))
            elif column == 1:
                if len(builder.thicknesses_m) > 0:
                    values = np.array(sorted(builder.thicknesses_m)) * 1e9
                    return ', '.join(locale.format(self.thickness_format, v) for v in values)

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        elif role == QtCore.Qt.UserRole:
            return builder

        elif role == QtCore.Qt.BackgroundRole:
            if len(builder) == 0:
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
        self._builders[row] = value

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

        builder = self._builders.pop(oldrow)
        self._builders.insert(newrow, builder)

        self.modelReset.emit()

        return True

    def isValid(self):
        return super().isValid() and all(len(b) > 0 for b in self._builders)

    def _add_builder(self, builder):
        self._builders.append(builder)

    def addLayerBuilder(self, builder):
        self._add_builder(builder)
        self.modelReset.emit()

    def addNewLayerBuilder(self):
        self.addLayerBuilder(LayerBuilder())

    def updateLayerBuilder(self, row, builder):
        self._builders[row] = builder
        self.modelReset.emit()

    def removeLayerBuilder(self, builder):
        if builder not in self._builders:
            return
        self._builders.remove(builder)
        self.modelReset.emit()

    def clearLayerBuilders(self):
        self._builders.clear()
        self.modelReset.emit()

    def hasLayerBuilders(self):
        return bool(self._builders)

    def layerBuilder(self, row):
        return self._builders[row]

    def layerBuilders(self):
        return tuple(self._builders)

    def setLayerBuilders(self, builders):
        self.clearLayerBuilders()
        for builder in builders:
            self._add_builder(builder)
        self.modelReset.emit()

    def availableMaterials(self):
        return self._available_materials

    def setAvailableMaterials(self, materials):
        for builder in self._builders:
            builder.materials = [m for m in materials if m in builder.materials]

        self._available_materials = materials

        self.modelReset.emit()

class LayerBuilderDelegate(QtWidgets.QItemDelegate):

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
        builder = model.layerBuilder(index.row())
        column = index.column()

        if column == 0:
            editor.setMaterials(self._available_materials)
            editor.setAllowVacuum(True)
            editor.setSelectedMaterials(builder.materials)

        elif column == 1:
            values = np.array(sorted(builder.thicknesses_m)) * 1e9
            editor.setValues(values)

    def setModelData(self, editor, model, index):
        column = index.column()
        builder = model.layerBuilder(index.row())

        if column == 0:
            builder.materials = editor.selectedMaterials()

        elif column == 1:
            values = editor.values()
            builder.thicknesses_m = set(np.array(values) * 1e-9)

        model.updateLayerBuilder(index.row(), builder)

    def availableMaterials(self):
        return self._available_materials

    def setAvailableMaterials(self, materials):
        self._available_materials.clear()
        self._available_materials.extend(materials)

class LayerBuilderToolbar(QtWidgets.QToolBar):

    def __init__(self, table, parent=None):
        super().__init__(parent)

        # Variables
        self.table = table

        # Actions
        self.act_add = self.addAction(QtGui.QIcon.fromTheme("list-add"), "Add")
        self.act_add.setToolTip('Add layer')

        self.act_remove = self.addAction(QtGui.QIcon.fromTheme("list-remove"), 'Remove')
        self.act_remove.setToolTip('Remove layer')
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
        has_rows = model.hasLayerBuilders()

        selection_model = self.table.selectionModel()
        has_selection = selection_model.hasSelection()

        self.act_remove.setEnabled(has_rows and has_selection)
        self.act_clear.setEnabled(has_rows)

    def _on_add_layer(self):
        model = self.table.model()
        model.addNewLayerBuilder()

    def _on_remove_layer(self):
        selection_model = self.table.selectionModel()
        if not selection_model.hasSelection():
            return

        indexes = selection_model.selectedIndexes()
        model = self.table.model()
        for row in reversed([index.row() for index in indexes]):
            builder = model.layerBuilder(row)
            model.removeLayerBuilder(builder)

    def _on_clear_layers(self):
        model = self.table.model()
        model.clearLayerBuilders()

class LayerBuilderWidget(QtWidgets.QWidget, Validable):

    layerBuildersChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__()

        # Variables
        model = LayerBuilderModel()

        # Widgets
        self.table = QtWidgets.QTableView()
        self.table.setModel(model)
        self.table.setItemDelegate(LayerBuilderDelegate())
        self.table.setWordWrap(True)
        self.table.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setDragDropMode(QtWidgets.QTableView.InternalMove)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)

        header = self.table.horizontalHeader()
        for column in range(model.columnCount()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)

        header.setStyleSheet('color: blue')

        self.toolbar = LayerBuilderToolbar(self.table)

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

        # Signals
        model.dataChanged.connect(self.layerBuildersChanged)
        model.modelReset.connect(self.layerBuildersChanged)

    def isValid(self):
        return self.table.model().isValid()

    def availableMaterials(self):
        return self.table.itemDelegate().availableMaterials()

    def setAvailableMaterials(self, materials):
        self.table.model().setAvailableMaterials(materials)
        self.table.itemDelegate().setAvailableMaterials(materials)

    def layerBuilders(self):
        return self.table.model().layerBuilders()

    def setLayerBuilders(self, builders):
        self.table.model().setLayerBuilders(builders)

#--- Base widgets

class SampleWidget(QtWidgets.QWidget, Validable, metaclass=QABCMeta):

    changed = QtCore.Signal()

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

    widget = LayerBuilderWidget()
    widget.setAvailableMaterials(materials)

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run_layerswidget()
