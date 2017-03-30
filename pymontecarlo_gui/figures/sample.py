""""""

# Standard library modules.
import sys
from math import pi

# Third party modules.
import matplotlib
matplotlib.use('qt5agg')
from matplotlib import figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QComboBox, QSlider, QRadioButton, QButtonGroup, QLabel

# Local modules.
from pymontecarlo.options.material import Material
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import \
    (SubstrateSample, InclusionSample, HorizontalLayerSample,
     VerticalLayerSample, SphereSample)
from pymontecarlo.options.sample.base import Layer
from pymontecarlo.figures.sample import SampleFigure, Perspective

# Globals and constants variables.
DS = Material('Ds', {110: 1.}, 1.)
RG = Material('Rg', {111: 1.}, 1.)
AU = Material('Au', {79: 1.}, 1.)
RE = Material('Re', {75: 1.}, 1.)
OS = Material('Os', {76: 1.}, 1.)
IR = Material('Ir', {77: 1.}, 1.)
PT = Material('Pt', {78: 1.}, 1.)

class QtPlt (QDialog):

    cos = 0
    sin = 0

    def __init__ (self):
        QDialog.__init__ (self)

        # matplotlib
        self._figure = figure.Figure()
        self._canvas = FigureCanvas(self._figure)
        self._toolbar = NavigationToolbar2QT(self._canvas, self)

        # comboboxes
        self._combo_sample = QComboBox()
        self._combo_sample.addItem('--- choose sample ---', None)
        self._combo_sample.addItem('SubstrateSample', SubstrateSample)
        self._combo_sample.addItem('InclusionSample', InclusionSample)
        self._combo_sample.addItem('HLayerSample', HorizontalLayerSample)
        self._combo_sample.addItem('VLayerSample', VerticalLayerSample)
        self._combo_sample.addItem('SphereSample', SphereSample)
        self._combo_sample.currentIndexChanged.connect(self.plot)

        self._combo_beam = QComboBox()
        self._combo_beam.addItem('--- choose beam ---', None)
        self._combo_beam.addItem('GaussianBeam', GaussianBeam)
        self._combo_beam.currentIndexChanged.connect(self.plot)

        self._combo_trajectory = QComboBox()
        self._combo_trajectory.addItem('--- choose trajectory ---', None)
        self._combo_trajectory.currentIndexChanged.connect(self.plot)

        # slider
        self._slider_tilt_deg = QSlider(Qt.Horizontal)
        self._slider_tilt_deg.setMinimum(-180)
        self._slider_tilt_deg.setMaximum(180)
        self._slider_tilt_deg.setValue(0)
        self._slider_tilt_deg.sliderReleased.connect(self.plot)

        self._slider_rotation_deg = QSlider(Qt.Horizontal)
        self._slider_rotation_deg.setMinimum(-180)
        self._slider_rotation_deg.setMaximum(180)
        self._slider_rotation_deg.setValue(0)
        self._slider_rotation_deg.sliderReleased.connect(self.plot)
        self._slider_rotation_deg.setDisabled(True)

        # radio buttons
        self._radio_xz = QRadioButton('XZ')
        self.radio_yz = QRadioButton('YZ')
        self.radio_xy = QRadioButton('XY')
        self._radio_xz.setChecked(True)

        self._radio_perspective = QButtonGroup()
        self._radio_perspective.addButton(self._radio_xz)
        self._radio_perspective.addButton(self.radio_yz)
        self._radio_perspective.addButton(self.radio_xy)
        self._radio_perspective.buttonClicked.connect(self.plot)

        # layout
        sublayout_combo = QHBoxLayout()
        sublayout_combo.addWidget(self._combo_sample)
        sublayout_combo.addWidget(self._combo_beam)
        sublayout_combo.addWidget(self._combo_trajectory)

        sublayout_perspective = QGridLayout()
        sublayout_perspective.addWidget(self._radio_xz, 1, 1)
        sublayout_perspective.addWidget(self.radio_yz, 2, 1)
        sublayout_perspective.addWidget(self.radio_xy, 3, 1)
        sublayout_perspective.addWidget(QLabel('tilt'), 1, 2)
        sublayout_perspective.addWidget(QLabel('rotation'), 2, 2)
        sublayout_perspective.addWidget(self._slider_tilt_deg, 1, 3)
        sublayout_perspective.addWidget(self._slider_rotation_deg, 2, 3)

        layout = QVBoxLayout()
        layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas)
        layout.addLayout(sublayout_combo)
        layout.addLayout(sublayout_perspective)
        self.setLayout(layout)

        self.plot()

    # def slider_event(self):
    #     pass

    def plot(self):
        deg2rad = lambda a: (a * 2. * pi) / 360.



        tilt_rad = deg2rad(self._slider_tilt_deg.value())
        rotation_rad = deg2rad(self._slider_rotation_deg.value())

        layer = [Layer(RE, .1), Layer(OS, .15),
                 Layer(IR, .2), Layer(PT, .05)]

        sample_cls = self._combo_sample.currentData()

        if sample_cls == SubstrateSample:
            sample = SubstrateSample(DS, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == InclusionSample:
            sample = InclusionSample(DS, AU, 0.5, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == HorizontalLayerSample:
            sample = HorizontalLayerSample(DS, layer, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        elif sample_cls == VerticalLayerSample:
            sample = VerticalLayerSample(DS, RG, layer, tilt_rad=tilt_rad,
                                         rotation_rad=rotation_rad)
        elif sample_cls == SphereSample:
            sample = SphereSample(AU, 0.5, tilt_rad=tilt_rad, rotation_rad=rotation_rad)
        else:
            sample = None

        beam_cls = self._combo_beam.currentData()

        if beam_cls == GaussianBeam:
            beams = [GaussianBeam(42., 0.05)]
        else:
            beams = []

        #trajectory_cls = self._combo_trajectory.currentData()

        # TODO handle trajectories
        trajectories = []

        sf = SampleFigure(sample, beams, trajectories)

        if self.radio_yz.isChecked():
            sf.perspective = Perspective.YZ
        elif self.radio_xy.isChecked():
            sf.perspective = Perspective.XY
        else:
            sf.perspective = Perspective.XZ

        self._figure.clf()

        ax = self._figure.add_subplot(111)
        sf.draw(ax=ax)

        self._canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pe = QtPlt()
    pe.show()

    sys.exit(app.exec_())
