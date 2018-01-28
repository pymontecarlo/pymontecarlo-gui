""""""

# Standard library modules.
import abc
from collections import namedtuple
import itertools

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

import numpy as np

# Local modules.
from pymontecarlo.options.beam.cylindrical import \
    CylindricalBeam, CylindricalBeamBuilder
from pymontecarlo.util.tolerance import tolerance_to_decimals

from pymontecarlo_gui.options.beam.base import BeamFieldBase, EnergyField, ParticleField
from pymontecarlo_gui.options.base import ToleranceMixin
from pymontecarlo_gui.widgets.field import \
    WidgetFieldBase, FieldBase, FieldChooser, MultiValueFieldBase
from pymontecarlo_gui.widgets.lineedit import \
    ColoredFloatLineEdit, ColoredMultiFloatLineEdit

# Globals and constants variables.

Position = namedtuple('Position', ('x_m', 'y_m'))

class DiameterField(MultiValueFieldBase, ToleranceMixin):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        self._widget.setValues([100.0])

        # Widgets
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Diameter(s) FWHM [nm]'

    def description(self):
        return 'The diameter corresponds to the full width at half maximum (FWHM) of a two dimensional Gaussian distribution'

    def widget(self):
        return self._widget

    def setToleranceMeter(self, tolerance_m):
        super().setToleranceMeter(tolerance_m)
        decimals = tolerance_to_decimals(tolerance_m * 1e9)
        self._widget.setRange(tolerance_m, float('inf'), decimals)

    def diametersMeter(self):
        return np.array(self._widget.values()) * 1e-9

    def setDiametersMeter(self, diameters_m):
        values = np.array(diameters_m) * 1e9
        self._widget.setValues(values)

class CoordinateField(FieldBase, ToleranceMixin):

    def __init__(self, title):
        self._title = title + ' [nm]'
        super().__init__()

        # Widgets
        self._widget = ColoredFloatLineEdit()
        self._widget.setValue(0.0)

        # Signals
        self._widget.valueChanged.connect(self.fieldChanged)

    def title(self):
        return self._title

    def widget(self):
        return self._widget

    def setToleranceMeter(self, tolerance_m):
        super().setToleranceMeter(tolerance_m)
        decimals = tolerance_to_decimals(tolerance_m * 1e9)
        self._widget.setRange(float('-inf'), float('inf'), decimals)

    def coordinateMeter(self):
        return self._widget.value() / 1e9

    def setCoordinateMeter(self, value_m):
        self._widget.setValue(value_m * 1e9)

class StepField(FieldBase):

    def __init__(self, title='Number of steps'):
        self._title = title
        super().__init__()

        # Widgets
        self._widget = ColoredFloatLineEdit()
        self._widget.setRange(2, 500, 0)
        self._widget.setValue(5)

        # Signals
        self._widget.valueChanged.connect(self.fieldChanged)

    def title(self):
        return self._title

    def widget(self):
        return self._widget

    def step(self):
        return self._widget.value()

    def setStep(self, step):
        self._widget.setValue(step)

class PositionField(WidgetFieldBase, ToleranceMixin):

    def __init__(self):
        super().__init__()

    def setToleranceMeter(self, tolerance_m):
        for field in self.fields():
            if hasattr(field, 'setToleranceMeter'):
                field.setToleranceMeter(tolerance_m)

    @abc.abstractmethod
    def positions(self):
        return []

class SinglePositionField(PositionField):

    def __init__(self):
        super().__init__()

        self.field_x = CoordinateField('x')
        self.addLabelField(self.field_x)

        self.field_y = CoordinateField('y')
        self.addLabelField(self.field_y)

    def title(self):
        return 'Single position'

    def positions(self):
        x_m = self.field_x.coordinateMeter()
        y_m = self.field_y.coordinateMeter()
        return [Position(x_m, y_m)]

class LineScanPositionField(PositionField):

    def __init__(self):
        super().__init__()

        self.field_start = CoordinateField('Start')
        self.field_start.setCoordinateMeter(-1e-6)
        self.addLabelField(self.field_start)

        self.field_stop = CoordinateField('Stop')
        self.field_stop.setCoordinateMeter(1e-6)
        self.addLabelField(self.field_stop)

        self.field_step = StepField()
        self.addLabelField(self.field_step)

class LineScanXPositionField(LineScanPositionField):

    def title(self):
        return 'Line scan along X axis'

    def positions(self):
        start_m = self.field_start.coordinateMeter()
        stop_m = self.field_stop.coordinateMeter()
        num = self.field_step.step()
        return [Position(x_m, 0.0)
                for x_m in np.linspace(start_m, stop_m, num, endpoint=True)]

class LineScanYPositionField(LineScanPositionField):

    def title(self):
        return 'Line scan along Y axis'

    def positions(self):
        start_m = self.field_start.coordinateMeter()
        stop_m = self.field_stop.coordinateMeter()
        num = self.field_step.step()
        return [Position(0.0, y_m)
                for y_m in np.linspace(start_m, stop_m, num, endpoint=True)]

class GridPositionField(PositionField):

    def __init__(self):
        super().__init__()

        self.field_x_start = CoordinateField('Start X')
        self.field_x_start.setCoordinateMeter(-1e-6)
        self.addLabelField(self.field_x_start)

        self.field_x_stop = CoordinateField('Stop X')
        self.field_x_stop.setCoordinateMeter(1e-6)
        self.addLabelField(self.field_x_stop)

        self.field_x_step = StepField('Number of steps X')
        self.addLabelField(self.field_x_step)

        self.field_y_start = CoordinateField('Start Y')
        self.field_y_start.setCoordinateMeter(-1e-6)
        self.addLabelField(self.field_y_start)

        self.field_y_stop = CoordinateField('Stop Y')
        self.field_y_stop.setCoordinateMeter(1e-6)
        self.addLabelField(self.field_y_stop)

        self.field_y_step = StepField('Number of steps Y')
        self.addLabelField(self.field_y_step)

    def title(self):
        return 'Grid'

    def positions(self):
        x_start_m = self.field_x_start.coordinateMeter()
        x_stop_m = self.field_x_stop.coordinateMeter()
        x_num = self.field_x_step.step()
        xs_m = np.linspace(x_start_m, x_stop_m, x_num, endpoint=True)

        y_start_m = self.field_y_start.coordinateMeter()
        y_stop_m = self.field_y_stop.coordinateMeter()
        y_num = self.field_y_step.step()
        ys_m = np.linspace(y_start_m, y_stop_m, y_num, endpoint=True)

        return [Position(x_m, y_m) for x_m, y_m in itertools.product(xs_m, ys_m)]

class PositionsModel(QtCore.QAbstractTableModel, ToleranceMixin):

    def __init__(self):
        super().__init__()

        self._positions = []

    def rowCount(self, parent=None):
        return len(self._positions)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        position = self._positions[row]

        if role == QtCore.Qt.DisplayRole:
            if self.toleranceMeter() is not None:
                precision = tolerance_to_decimals(self.toleranceMeter()) - 9
                fmt = '{0:.{precision}f}'
            else:
                fmt = '{0:g}'

            if column == 0:
                return fmt.format(position.x_m * 1e9, precision=precision)
            elif column == 1:
                return fmt.format(position.y_m * 1e9, precision=precision)

        elif role == QtCore.Qt.UserRole:
            return position

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

    def headerData(self, section , orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return 'X [nm]'
                elif section == 1:
                    return 'Y [nm]'

            elif orientation == QtCore.Qt.Vertical:
                return str(section + 1)

    def flags(self, index):
        return super().flags(index)

    def _add_position(self, position):
        if position in self._positions:
            return False
        self._positions.append(position)
        return True

    def addPosition(self, position):
        added = self._add_position(position)
        if added:
            self.modelReset.emit()
        return added

    def addPositions(self, positions):
        if not positions:
            return False

        added = False
        for position in positions:
            added |= self._add_position(position)

        if added:
            self.modelReset.emit()

        return added

    def removePosition(self, position):
        if position not in self._positions:
            return False
        self._positions.remove(position)
        self.modelReset.emit()
        return True

    def clearPositions(self):
        self._positions.clear()
        self.modelReset.emit()

    def hasPositions(self):
        return bool(self._positions)

    def position(self, row):
        return self._positions[row]

    def positions(self):
        return tuple(self._positions)

    def setPositions(self, positions):
        self.clearPositions()
        for x, y in positions:
            self._add_position(x, y)
        self.modelReset.emit()

    def setToleranceMeter(self, tolerance_m):
        super().setToleranceMeter(tolerance_m)
        self.modelReset.emit()

class PositionsWidget(QtWidgets.QWidget, ToleranceMixin):

    positionsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        model = PositionsModel()
        model.addPosition(Position(0.0, 0.0))

        # Actions
        self.action_remove = QtWidgets.QAction('Remove')
        self.action_remove.setIcon(QtGui.QIcon.fromTheme('list-remove'))
        self.action_remove.setToolTip('Remove position')
        self.action_remove.setEnabled(False)

        self.action_clear = QtWidgets.QAction('Clear')
        self.action_clear.setIcon(QtGui.QIcon.fromTheme('edit-clear'))
        self.action_clear.setToolTip('Remove all positions')
        self.action_clear.setEnabled(False)

        # Widgets
        self.chooser = FieldChooser()

        self.button_add = QtWidgets.QPushButton('Add position(s)')
        self.button_add.setIcon(QtGui.QIcon.fromTheme('list-add'))
        self.button_add.setMaximumWidth(self.button_add.sizeHint().width())

        self.table_positions = QtWidgets.QTableView()
        self.table_positions.setModel(model)
        self.table_positions.setSelectionBehavior(QtWidgets.QTableView.SelectRows)

        header = self.table_positions.horizontalHeader()
        for column in range(model.columnCount()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addAction(self.action_remove)
        self.toolbar.addAction(self.action_clear)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.chooser)
        layout.addWidget(self.button_add, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(self.table_positions)
        layout.addWidget(self.toolbar, alignment=QtCore.Qt.AlignRight)
        self.setLayout(layout)

        # Signals
        self.action_remove.triggered.connect(self._on_remove_triggered)
        self.action_clear.triggered.connect(self._on_clear_triggered)

        self.button_add.clicked.connect(self._on_add_clicked)

        model.dataChanged.connect(self._on_positions_changed)
        model.dataChanged.connect(self.positionsChanged)
        model.modelReset.connect(self._on_positions_changed)
        model.modelReset.connect(self.positionsChanged)
        self.table_positions.selectionModel().selectionChanged.connect(self._on_positions_changed)

    def _on_remove_triggered(self):
        selection_model = self.table_positions.selectionModel()
        if not selection_model.hasSelection():
            return

        indexes = selection_model.selectedIndexes()
        model = self.table_positions.model()
        for row in reversed(sorted(set(index.row() for index in indexes))):
            model.removePosition(model.position(row))

    def _on_clear_triggered(self):
        model = self.table_positions.model()
        model.clearPositions()

    def _on_add_clicked(self):
        field = self.chooser.currentField()
        if field is None:
            return

        positions = field.positions()
        self.table_positions.model().addPositions(positions)

    def _on_positions_changed(self):
        model = self.table_positions.model()
        has_rows = model.hasPositions()

        selection_model = self.table_positions.selectionModel()
        has_selection = selection_model.hasSelection()

        self.action_remove.setEnabled(has_rows and has_selection)
        self.action_clear.setEnabled(has_rows)

    def _on_field_changed(self):
        field = self.chooser.currentField()
        if field is None:
            return
        self.button_add.setEnabled(field.isValid())

    def setToleranceMeter(self, tolerance_m):
        super().setToleranceMeter(tolerance_m)

        for field in self.chooser.fields():
            field.setToleranceMeter(tolerance_m)

        self.table_positions.model().setToleranceMeter(tolerance_m)

    def registerPositionField(self, field):
        self.chooser.addField(field)
        field.fieldChanged.connect(self._on_field_changed)

    def positions(self):
        return self.table_positions.model().positions()

class PositionsField(FieldBase, ToleranceMixin):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = PositionsWidget()

        # Signals
        self._widget.positionsChanged.connect(self.fieldChanged)

    def title(self):
        return 'Positions'

    def widget(self):
        return self._widget

    def registerPositionField(self, field):
        field.setToleranceMeter(self.toleranceMeter())
        self._widget.registerPositionField(field)

    def positions(self):
        return self._widget.positions()

    def setToleranceMeter(self, tolerance_m):
        super().setToleranceMeter(tolerance_m)
        self._widget.setToleranceMeter(tolerance_m)

class CylindricalBeamField(BeamFieldBase):

    def __init__(self):
        super().__init__()

        self.field_energy = EnergyField()
        self.addLabelField(self.field_energy)

        self.field_particle = ParticleField()
        self.addLabelField(self.field_particle)

        self.field_diameter = DiameterField()
        self.field_diameter.setToleranceMeter(CylindricalBeam.DIAMETER_TOLERANCE_m)
        self.field_diameter.setDiametersMeter([10e-9])
        self.addLabelField(self.field_diameter)

        self.field_position = PositionsField()
        self.field_position.setToleranceMeter(CylindricalBeam.POSITION_TOLERANCE_m)
        self.field_position.registerPositionField(SinglePositionField())
        self.field_position.registerPositionField(LineScanXPositionField())
        self.field_position.registerPositionField(LineScanYPositionField())
        self.field_position.registerPositionField(GridPositionField())

        self.addGroupField(self.field_position)

    def title(self):
        return 'Cylindrical beam'

    def description(self):
        return 'Incident particles distributed randomly within a circle'

    def _create_builder(self):
        return CylindricalBeamBuilder()

    def beams(self):
        builder = self._create_builder()

        for energy_eV in self.field_energy.energiesEV():
            builder.add_energy_eV(energy_eV)

        builder.add_particle(self.field_particle.particle())

        for diameter_m in self.field_diameter.diametersMeter():
            builder.add_diameter_m(diameter_m)

        for position in self.field_position.positions():
            builder.add_position(position.x_m, position.y_m)

        return super().beams() + builder.build()
