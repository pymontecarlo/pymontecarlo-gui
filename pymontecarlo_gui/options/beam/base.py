#!/usr/bin/env python3
""""""

# Standard library modules.
import sys

# Third party modules.
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, \
    QRadioButton, QButtonGroup, QLineEdit
from PyQt5.QtGui import QDoubleValidator

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
        self._energyEdit.setValidator(QDoubleValidator(0., 1., 2)) # TODO find default values
        self._energyEdit.textChanged.connect(self._energyChanged)

        # Diameter
        self._diameterLabel = QLabel('Diameter:')
        self._diameterEdit = QLineEdit()
        self._diameterEdit.setValidator(QDoubleValidator(0., 1., 2))  # TODO find default values
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
    # bsw.show()

    sys.exit(app.exec_())
