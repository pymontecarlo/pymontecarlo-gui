#!/usr/bin/env python3
""""""

# Standard library modules.
import sys

# Third party modules.
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, \
    QComboBox, QRadioButton, QButtonGroup, QLineEdit, QTableWidget
from PyQt5.QtGui import QDoubleValidator, QIntValidator

# Local modules.
# from pymontecarlo.options.beam import GaussianBeam

# Globals and constants variables.

class BeamWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        # Type
        self._typeLabel = QLabel('Type:')
        self._typeCombo = QComboBox()
        self._typeCombo.addItem('-- Select Beam --', None)
        self._typeCombo.addItem('GaussianBeam', None)
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

class BeamPositionWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        # Initial positions
        self._titleLabel = QLabel('Initial positions')

        # Add scan
        self._addLabel = QLabel('Add:')
        self._addCombo = QComboBox()
        self._addCombo.addItem('-- Select Scan --', None)
        self._addCombo.addItem('Line Scan', None)
        self._addCombo.currentIndexChanged.connect(self._scanChanged)

        # Start / end / steps (ses)
        self._sesXLabel = QLabel('X')
        self._sesYLabel = QLabel('Y')
        self._sesStartLabel = QLabel('Start')
        self._sesEndLabel = QLabel('End')
        self._sesStepsLabel = QLabel('Steps')
        # TODO add slots
        self._sesXStartEdit = QLineEdit()
        self._sesXStartEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO parameters?
        self._sesYStartEdit = QLineEdit()
        self._sesYStartEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO parameters?
        self._sesXEndEdit = QLineEdit()
        self._sesXEndEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO parameters?
        self._sesYEndEdit = QLineEdit()
        self._sesYEndEdit.setValidator(QDoubleValidator(0., 1, 2))  # TODO parameters?
        self._sesStepsEdit = QLineEdit()
        self._sesStepsEdit.setValidator(QIntValidator(0, 10))  # TODO parameters?

        # Table
        self._scansTable = QTableWidget()

        # Layout
        addLayout = QHBoxLayout()
        addLayout.addWidget(self._addLabel)
        addLayout.addWidget(self._addCombo)

        sesLayout = QGridLayout()
        sesLayout.addWidget(self._sesXLabel, 0, 1)
        sesLayout.addWidget(self._sesYLabel, 0, 2)
        sesLayout.addWidget(self._sesStartLabel, 1, 0)
        sesLayout.addWidget(self._sesEndLabel, 2, 0)
        sesLayout.addWidget(self._sesStepsLabel, 1, 3)
        sesLayout.addWidget(self._sesXStartEdit, 1, 1)
        sesLayout.addWidget(self._sesYStartEdit, 1, 2)
        sesLayout.addWidget(self._sesXEndEdit, 2, 1)
        sesLayout.addWidget(self._sesYEndEdit, 2, 2)
        sesLayout.addWidget(self._sesStepsEdit, 1, 4)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._titleLabel)
        mainLayout.addLayout(addLayout)
        mainLayout.addLayout(sesLayout)
        mainLayout.addWidget(self._scansTable)

        self.setLayout(mainLayout)

    def _scanChanged(self):
        print('scan changed')

    def positions(self):
        """
        Returns a :class:`list` of :class:`tuple` for the x and y positions.
        """
        return []


if __name__ == "__main__":
    app = QApplication(sys.argv)

    bw = BeamWidget()
    bsw = BeamPositionWidget()

    bw.show()
    bsw.show()

    sys.exit(app.exec_())
