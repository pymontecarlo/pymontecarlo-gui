#!/usr/bin/env python3
""""""

# Standard library modules.
import sys
import enum

# Third party modules.
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QAbstractListModel
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, \
    QComboBox, QRadioButton, QButtonGroup, QLineEdit, QTableView, QPushButton, QAbstractItemView, \
    QListView
from PyQt5.QtGui import QDoubleValidator, QIntValidator

# Local modules.
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.particle import Particle

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

        # Particle
        self._particleLabel = QLabel('Particle:')
        self._particleRadioElectron = QRadioButton('Electron')
        self._particleRadioElectron.setChecked(True)
        self._particleRadioPhoton = QRadioButton('Photon')

        self._particleGroup = QButtonGroup()
        self._particleGroup.addButton(self._particleRadioElectron)
        self._particleGroup.addButton(self._particleRadioPhoton)

        # Initial energy
        self._energyLabel = QLabel('Initial Energy:')
        self._energyEdit = QLineEdit()
        self._energyEdit.setValidator(QDoubleValidator(0., 1., 2))  # TODO default values for parameters?

        # Diameter
        self._diameterLabel = QLabel('Diameter:')
        self._diameterEdit = QLineEdit()
        self._diameterEdit.setValidator(QDoubleValidator(0., 1., 2))  # TODO -""-

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

    def beams(self, positions=()):
        """
        :param positions: :class:`list` of :class:`tuple` of :class:`float` 
        :return a :class:`list` of :class:`Beam`.
        """
        beams = list()

        for x0_m, y0_m in positions:
            energy_eV = self._energyEdit.text()
            diameter_m = self._diameterEdit.text()
            particle = Particle.ELECTRON if self._particleRadioElectron.isChecked() \
                else Particle.PHOTON

            try:
                b = self._typeCombo.currentData()(energy_eV=energy_eV, diameter_m=diameter_m,
                                                  particle=particle, x0_m=x0_m, y0_m=y0_m)
                beams.append(b)
            except Exception as _:
                # TODO user my be warned
                pass

            return beams


class _Scan():
    def __init__(self, start, end, steps, length=None):
        """
        :param start: :class:`tuple` of :class:`float`
        :param end: :class:`tuple` of :class:`float`
        :param steps: :class:`int`. Note that steps+1 positions will result of that.
        """
        self._startX, self._startY = start
        self._endX, self._endY = end
        self._steps = steps

        if length is None:
            self._length = steps
        else:
            self._length = length

    def __str__(self):
        raise NotImplementedError

    def __len__(self):
        return self._length

    def __getitem__(self, i):
        raise NotImplementedError

    def positions(self):
        """
        :return: :class:`Generator` that returns :class:`tuple` of :class:`float`
        """
        for i in range(len(self)):
            yield self.__getitem__(i)

    edit = __init__


class _PointScan(_Scan):
    def __init__(self, start):
        _Scan.__init__(self, start, (None, None), 1)

    def __str__(self):
        return 'Point Scan ({}, {})'.format(self._startX, self._startY)

    def __getitem__(self, _):
        return self._startX, self._startY


class _LineScan(_Scan):
    def __init__(self, start, end, steps):
        _Scan.__init__(self, start, end, steps, length=steps + 1)

    def __str__(self):
        return 'Line Scan (({}, {}), ({}, {}), {})'.format(self._startX, self._startY, self._endX,
                                                           self._endY, self._steps)

    def __getitem__(self, i):
        xi = self._startX + (self._endX - self._startX) * i / self._steps
        yi = self._startY + (self._endY - self._startY) * i / self._steps
        return xi, yi


class _GridScan(_Scan):
    def __init__(self, start, end, stepsX, stepsY):
        _Scan.__init__(self, start, end, (stepsX + 1) * (stepsY + 1))
        self._stepsX = stepsX
        self._stepsY = stepsY

    def __str__(self):
        return 'Grid Scan (({}, {}), ({}, {}), ({}, {}))'.format(self._startX, self._startY,
                                                                 self._endX, self._endY,
                                                                 self._stepsX, self._stepsY)

    def __getitem__(self, i):
        ix = i % (self._stepsX + 1)
        iy = i // (self._stepsX + 1)
        xi = self._startX + (self._endX - self._startX) * ix / self._stepsX
        yi = self._startY + (self._endY - self._startY) * iy / self._stepsY
        return xi, yi

class _Positions():
    def __init__(self):
        self._scans = []

    def __len__(self):
        return sum((len(s) for s in self._scans))

    def __getitem__(self, i):
        # TODO improve documentation
        """
        :param i: :class:`int`
        :return: :class:`tuple` of :class:`float`
        """
        item, scan = self.getScan(i)
        return scan[item]

    @property
    def scans(self):
        return self._scans

    def positions(self):
        """
        Iterate over all positions of all scans belonging to this instance.
        :return: :class:`Generator` that returns :class:`tuple` of :class:`float`
        """
        for i in range(len(self)):
            yield self.__getitem__(i)

    def getScan(self, i):
        # TODO improve documentation
        """
        :param i: index of a position within a scan you want to access
        :return: :class:`tuple` containing corresponding internal :class:`int` index of scan and
        :class:`_Scan` itself
        """
        if i >= len(self):
            raise ValueError('Index is out of range')

        for s in self._scans:
            if i < len(s):
                return i, s
            i -= len(s)

        return None

    def addScan(self, scan):
        """
        :param scan: :class:`_Scan`
        """
        if not isinstance(scan, _Scan):
            raise ValueError('scan must be of type \'_Scan\'')
        self._scans.append(scan)

    def remScan(self, i):
        """
        :param i: :class:`int`
        """
        try:
            _, s = self.getScan(i)
            self._scans.remove(s)
        except Exception as _:
            self._scans.remove(i)


class _PositionsListModel(QAbstractListModel):
    def __init__(self, positions, parent=None, *args):
        QAbstractListModel.__init__(self, parent)

        if positions is None:
            raise ValueError('Positions cannot be None')

        self._positions = positions

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._positions.scans)

    def data(self, index, role=None):
        if index.isValid() and role == Qt.DisplayRole:
            return QVariant(str(self._positions.scans[index.row()]))
        else:
            return QVariant()


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
        self._addScanCombo.addItem('Point Scan', _PointScan)
        self._addScanCombo.addItem('Line Scan', _LineScan)
        self._addScanCombo.addItem('Grid Scan', _GridScan)

        # Start / end / steps (ses)
        self._sesXLabel = QLabel('X')
        self._sesYLabel = QLabel('Y')
        self._sesTotalLabel = QLabel('Total')
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
        self._sesStepsXEdit = QLineEdit()
        self._sesStepsXEdit.setValidator(QIntValidator(0, 10))  # TODO -"-
        self._sesStepsYEdit = QLineEdit()
        self._sesStepsYEdit.setValidator(QIntValidator(0, 10))  # TODO -"-
        self._sesStepsEdit = QLineEdit()
        self._sesStepsEdit.setValidator(QIntValidator(0, 10))  # TODO -"-

        # Table
        self._positions = _Positions()
        self._positions.addScan(_PointScan((0, 0)))  # TODO remove
        self._positions.addScan(_LineScan((0, 0), (4, 8), 2))  # TODO -"-
        self._positions.addScan(_GridScan((0, 0), (3, 6), 3, 3))  # TODO -"-

        self._scansTable = QTableView()
        self._scansTableModel = _PositionsTableModel(self._positions)
        self._scansTable.setModel(self._scansTableModel)
        self._scansTable.selectionModel()
        self._scansTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._scansTable.setSelectionMode(QAbstractItemView.NoSelection)

        self._scansList = QListView()
        self._scansListModel = _PositionsListModel(self._positions)
        self._scansList.setModel(self._scansListModel)

        # TODO native icons instead of text
        self._posAddButton = QPushButton('Add')
        self._posRemoveButton = QPushButton('Remove')
        self._posEditButton = QPushButton('Edit')


        # Layout
        addLayout = QHBoxLayout()
        addLayout.addWidget(self._addScanLabel)
        addLayout.addWidget(self._addScanCombo)

        sesLayout = QGridLayout()
        sesLayout.addWidget(self._sesXLabel, 0, 1)
        sesLayout.addWidget(self._sesYLabel, 0, 2)
        sesLayout.addWidget(self._sesTotalLabel, 0, 3)
        sesLayout.addWidget(self._sesStartLabel, 1, 0)
        sesLayout.addWidget(self._sesEndLabel, 2, 0)
        sesLayout.addWidget(self._sesStepsLabel, 3, 0)
        sesLayout.addWidget(self._sesStartXEdit, 1, 1)
        sesLayout.addWidget(self._sesStartYEdit, 1, 2)
        sesLayout.addWidget(self._sesEndXEdit, 2, 1)
        sesLayout.addWidget(self._sesEndYEdit, 2, 2)
        sesLayout.addWidget(self._sesStepsXEdit, 3, 1)
        sesLayout.addWidget(self._sesStepsYEdit, 3, 2)
        sesLayout.addWidget(self._sesStepsEdit, 3, 3)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self._posAddButton)
        buttonLayout.addWidget(self._posEditButton)
        buttonLayout.addWidget(self._posRemoveButton)

        viewsLayout = QHBoxLayout()
        viewsLayout.addWidget(self._scansList)
        viewsLayout.addWidget(self._scansTable)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._titleLabel)
        mainLayout.addLayout(addLayout)
        mainLayout.addLayout(sesLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addLayout(viewsLayout)

        self.setLayout(mainLayout)

        # Signals / Slots
        self._addScanCombo.currentIndexChanged.connect(self._scanChanged)
        self._posAddButton.clicked.connect(self._addScan)
        self._posRemoveButton.clicked.connect(self._removeScan)
        self._posEditButton.clicked.connect(self._editScan)
        # self._scansTable.selectionModel().selectionChanged.connect(self._selectionChanged)
        self._scansList.selectionModel().selectionChanged.connect(self._selectionChanged)

        # other
        self._sesInputMode(None)

    def _sesInputMode(self, scanClass=None):
        if scanClass is _PointScan:
            self._sesStartXEdit.setDisabled(False)
            self._sesStartYEdit.setDisabled(False)
            self._sesEndXEdit.setDisabled(True)
            self._sesEndYEdit.setDisabled(True)
            self._sesStepsXEdit.setDisabled(True)
            self._sesStepsYEdit.setDisabled(True)
            self._sesStepsEdit.setDisabled(True)

        elif scanClass is _LineScan:
            self._sesStartXEdit.setDisabled(False)
            self._sesStartYEdit.setDisabled(False)
            self._sesEndXEdit.setDisabled(False)
            self._sesEndYEdit.setDisabled(False)
            self._sesStepsXEdit.setDisabled(True)
            self._sesStepsYEdit.setDisabled(True)
            self._sesStepsEdit.setDisabled(False)

        elif scanClass is _GridScan:
            self._sesStartXEdit.setDisabled(False)
            self._sesStartYEdit.setDisabled(False)
            self._sesEndXEdit.setDisabled(False)
            self._sesEndYEdit.setDisabled(False)
            self._sesStepsXEdit.setDisabled(False)
            self._sesStepsYEdit.setDisabled(False)
            self._sesStepsEdit.setDisabled(True)

        else:
            self._sesStartXEdit.setDisabled(True)
            self._sesStartYEdit.setDisabled(True)
            self._sesEndXEdit.setDisabled(True)
            self._sesEndYEdit.setDisabled(True)
            self._sesStepsXEdit.setDisabled(True)
            self._sesStepsYEdit.setDisabled(True)
            self._sesStepsEdit.setDisabled(True)

    def _sesLoadData(self, scan=None):
        scanClass = scan.__class__
        startX = ''
        startY = ''
        endX = ''
        endY = ''
        stepsX = ''
        stepsY = ''
        steps = ''

        if scanClass is _PointScan:
            startX = str(scan._startX)
            startY = str(scan._startY)

        elif scanClass is _LineScan:
            startX = str(scan._startX)
            startY = str(scan._startY)
            endX = str(scan._endX)
            endY = str(scan._endY)
            steps = str(scan._steps)

        elif scanClass is _GridScan:
            startX = str(scan._startX)
            startY = str(scan._startY)
            endX = str(scan._endX)
            endY = str(scan._endY)
            stepsX = str(scan._stepsX)
            stepsY = str(scan._stepsY)

        self._sesStartXEdit.setText(startX)
        self._sesStartYEdit.setText(startY)
        self._sesEndXEdit.setText(endX)
        self._sesEndYEdit.setText(endY)
        self._sesStepsXEdit.setText(stepsX)
        self._sesStepsYEdit.setText(stepsY)
        self._sesStepsEdit.setText(steps)

    def _scanChanged(self):
        cd = self._addScanCombo.currentData()
        self._sesInputMode(cd)

    def _addScan(self):
        def myParse(lineEdit, type_=float):
            try:
                return type_(lineEdit.text())
            except:
                return 0

        startX = myParse(self._sesStartXEdit)
        startY = myParse(self._sesStartYEdit)
        endX = myParse(self._sesEndXEdit)
        endY = myParse(self._sesEndYEdit)
        stepsX = myParse(self._sesStepsXEdit, int)
        stepsY = myParse(self._sesStepsYEdit, int)
        steps = myParse(self._sesStepsEdit, int)

        try:
            self._scansTableModel.modelAboutToBeReset.emit()

            cd = self._addScanCombo.currentData()

            if cd is _PointScan:
                scan = _PointScan((startX, startY))
            elif cd is _LineScan:
                scan = _LineScan((startX, startY), (endX, endY), steps)
            elif cd is _GridScan:
                scan = _GridScan((startX, startY), (endX, endY), stepsX, stepsY)
            else:
                return

            self._positions.addScan(scan)
            self._scansListModel.modelReset.emit()
            self._scansTableModel.modelReset.emit()

        except:
            # TODO user may be warned that input was incorrect
            pass

    def _editScan(self):
        print('edit scan')

    def _removeScan(self):
        sm = self._scansList.selectionModel()
        s = sm.selection()
        i = s.indexes()
        print(i)

    def _selectionChanged(self, selected, deselected):
        if len(selected.indexes()) > 0:
            scan = self._positions.scans[selected.indexes()[0].row()]
            self._sesInputMode(scan.__class__)
            self._sesLoadData(scan)

    def positions(self):
        """
        Returns a :class:`list` of :class:`tuple` for the x and y positions.
        """
        return list(self._positions.positions())


def testScans():
    ps = _PointScan((4, 2))
    ls = _LineScan((1, 1), (2, 2), 2)
    gs = _GridScan((0, 0), (4, 2), 2, 2)

    print('ps:', list(ps.positions()))
    print('ls:', list(ls.positions()))
    print('gs:', list(gs.positions()))


if __name__ == "__main__":
    # testScans()
    app = QApplication(sys.argv)

    # bw = BeamWidget()
    bsw = BeamPositionWidget()

    # bw.show()
    bsw.show()

    sys.exit(app.exec_())
