#!/usr/bin/env python3
""""""

# Standard library modules.
import sys
import enum

# Third party modules.
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, \
    QComboBox, QRadioButton, QButtonGroup, QLineEdit, QTableView, QPushButton
from PyQt5.QtGui import QDoubleValidator, QIntValidator

# Local modules.
from pymontecarlo.options.beam import GaussianBeam

# Globals and constants variables.


class BeamWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        # Type
        self._typeLabel = QLabel('Type:')
        self._typeCombo = QComboBox()
        self._typeCombo.addItem('-- Select Beam --', None)
        self._typeCombo.addItem('GaussianBeam', GaussianBeam)
        self._typeCombo.currentIndexChanged.connect(self._beamChanged)

        # Particle
        self._particleLabel = QLabel('Particle:')
        self._particleRadioElectron = QRadioButton('Electron')
        self._particleRadioElectron.setChecked(True)
        self._particleRadioPhoton = QRadioButton('Photon')

        self._particleGroup = QButtonGroup()
        self._particleGroup.addButton(self._particleRadioElectron)
        self._particleGroup.addButton(self._particleRadioPhoton)
        self._particleGroup.buttonClicked.connect(self._particleChanged)

        # Initial energy
        self._energyLabel = QLabel('Initial Energy:')
        self._energyEdit = QLineEdit()
        self._energyEdit.setValidator(QDoubleValidator(0., 1., 2))  # TODO parameters?
        self._energyEdit.textChanged.connect(self._energyChanged)

        # Diameter
        self._diameterLabel = QLabel('Diameter:')
        self._diameterEdit = QLineEdit()
        self._diameterEdit.setValidator(QDoubleValidator(0., 1., 2))  # TODO parameters?
        self._diameterEdit.textChanged.connect(self._diameterChanged)

        # Layout
        typeLayout = QHBoxLayout()
        typeLayout.addWidget(self._typeLabel)
        typeLayout.addWidget(self._typeCombo)

        particleLayout = QHBoxLayout()
        particleLayout.addWidget(self._particleLabel)
        particleLayout.addWidget(self._particleRadioElectron)
        particleLayout.addWidget(self._particleRadioPhoton)

        energyLayout = QHBoxLayout()
        energyLayout.addWidget(self._energyLabel)
        energyLayout.addWidget(self._energyEdit)

        diameterLabel = QHBoxLayout()
        diameterLabel.addWidget(self._diameterLabel)
        diameterLabel.addWidget(self._diameterEdit)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(typeLayout)
        mainLayout.addLayout(particleLayout)
        mainLayout.addLayout(energyLayout)
        mainLayout.addLayout(diameterLabel)

        self.setLayout(mainLayout)

    def _beamChanged(self):
        print('beam changed')

    def _particleChanged(self):
        print('particle changed')

    def _energyChanged(self):
        print('energy changed')

    def _diameterChanged(self):
        print('diameter changed')

    def beams(self):
        """
        Returns a :class:`list` of :class:`Beam`.
        """
        return []


class _Scan():
    def __init__(self, start, end, steps):
        # self._start = start
        # self._end = end
        self._startX, self._startY = start
        self._endX, self._endY = end
        self._steps = steps

        # TODO we may add a buffered mode where positions are stored and can be modified

    def __len__(self):
        return self._steps + 1

    def __getitem__(self, item):
        raise NotImplementedError

    def positions(self):
        for i in range(len(self)):
            yield self.__getitem__(i)

    edit = __init__


class _LineScan(_Scan):
    def __getitem__(self, item):
        xi = self._startX + (self._endX - self._startX) * item / self._steps
        yi = self._startY + (self._endY - self._startY) * item / self._steps
        return xi, yi


class _Positions():
    def __init__(self):
        self._scans = []

    def __len__(self):
        return sum((len(s) for s in self._scans))

    def __getitem__(self, item):
        item, scan = self.getScan(item)
        return scan[item]

    def positions(self):
        for i in range(len(self)):
            yield self.__getitem__(i)

    def getScan(self, item):
        if item >= len(self):
            raise ValueError('Index is out of range')

        for s in self._scans:
            if item < len(s):
                return item, s
            item -= len(s)

        return None

    def addScan(self, scan):
        if not isinstance(scan, _Scan):
            raise ValueError('scan must be of type \'_Scan\'')
        self._scans.append(scan)

    def remScan(self, item):
        try:
            _, s = self.getScan(item)
            self._scans.remove(s)
        except Exception as _:
            self._scans.remove(item)


class _PositionsTableModel(QAbstractTableModel):
    def __init__(self, positions, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)

        if positions is None:
            raise ValueError('Positions cannot be None')

        self._positions = positions

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._positions)

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(str(self._positions[index.row()][index.column()]))

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(('X', 'Y')[col])
        return QVariant()

    # def flags(self, QModelIndex):
    #     # TODO handle selection
    #     pass


class BeamPositionWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        # Initial positions
        self._titleLabel = QLabel('Initial positions')

        # Add scan
        self._addScanLabel = QLabel('Add:')
        self._addScanCombo = QComboBox()
        self._addScanCombo.addItem('-- Select Scan --', None)
        self._addScanCombo.addItem('Line Scan', _LineScan)

        # Start / end / steps (ses)
        self._sesXLabel = QLabel('X')
        self._sesYLabel = QLabel('Y')
        self._sesStartLabel = QLabel('Start')
        self._sesEndLabel = QLabel('End')
        self._sesStepsLabel = QLabel('Steps')
        self._sesStartXEdit = QLineEdit()
        self._sesStartXEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO default values for parameters?
        self._sesStartYEdit = QLineEdit()
        self._sesStartYEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO -"-
        self._sesEndXEdit = QLineEdit()
        self._sesEndXEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO -"-
        self._sesEndYEdit = QLineEdit()
        self._sesEndYEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO -"-
        self._sesStepsEdit = QLineEdit()
        self._sesStepsEdit.setValidator(QIntValidator(0, 10))  # TODO -"-

        # Table
        self._positions = _Positions()
        self._positions.addScan(_LineScan((0, 0), (3, 3), 3))
        self._positions.addScan(_LineScan((0, 0), (4, 8), 2))
        self._positions.addScan(_LineScan((0, 0), (3, 6), 3))
        self._scansTable = QTableView()
        self._scansTableModel = _PositionsTableModel(self._positions)
        self._scansTable.setModel(self._scansTableModel)
        # TODO native icons instead of text
        self._posAddButton = QPushButton('Add')
        self._posAddButton.clicked.connect(self._addScan)
        self._posRemoveButton = QPushButton('Remove')
        self._posRemoveButton.clicked.connect(self._removeScan)
        self._posEditButton = QPushButton('Edit')
        self._posEditButton.clicked.connect(self._editScan)

        # Layout
        addLayout = QHBoxLayout()
        addLayout.addWidget(self._addScanLabel)
        addLayout.addWidget(self._addScanCombo)

        sesLayout = QGridLayout()
        sesLayout.addWidget(self._sesXLabel, 0, 1)
        sesLayout.addWidget(self._sesYLabel, 0, 2)
        sesLayout.addWidget(self._sesStartLabel, 1, 0)
        sesLayout.addWidget(self._sesEndLabel, 2, 0)
        sesLayout.addWidget(self._sesStepsLabel, 1, 3)
        sesLayout.addWidget(self._sesStartXEdit, 1, 1)
        sesLayout.addWidget(self._sesStartYEdit, 1, 2)
        sesLayout.addWidget(self._sesEndXEdit, 2, 1)
        sesLayout.addWidget(self._sesEndYEdit, 2, 2)
        sesLayout.addWidget(self._sesStepsEdit, 1, 4)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self._posAddButton)
        buttonLayout.addWidget(self._posEditButton)
        buttonLayout.addWidget(self._posRemoveButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._titleLabel)
        mainLayout.addLayout(addLayout)
        mainLayout.addLayout(sesLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self._scansTable)

        self.setLayout(mainLayout)

        # Signals / Slots
        self._scansTable.selectionModel().selectionChanged.connect(self._selectionChanged)

    def _addScan(self):
        try:
            self._scansTableModel.modelAboutToBeReset.emit()

            startX = int(self._sesStartXEdit.text())
            startY = int(self._sesStartYEdit.text())
            endX = int(self._sesEndXEdit.text())
            endY = int(self._sesEndYEdit.text())
            steps = int(self._sesStepsEdit.text())
            scan = self._addScanCombo.currentData()((startX, startY), (endX, endY), steps)
            self._positions.addScan(scan)

            self._scansTableModel.modelReset.emit()
        except Exception as _:
            # TODO user may be warned that input was incorrect
            pass

    def _selectionChanged(self, selected, deselected):
        print('selection changed')

    def _editScan(self):
        print('edit scan')

    def _removeScan(self):
        print('remove scan')

    def positions(self):
        """
        Returns a :class:`list` of :class:`tuple` for the x and y positions.
        """
        return list(self._positions.positions())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # bw = BeamWidget()
    bsw = BeamPositionWidget()

    # bw.show()
    bsw.show()

    sys.exit(app.exec_())
