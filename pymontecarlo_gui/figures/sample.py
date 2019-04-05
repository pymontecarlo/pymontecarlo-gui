""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

import matplotlib
matplotlib.use('qt5agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib_scalebar.scalebar import ScaleBar

# Local modules.
from pymontecarlo.figures.sample import SampleFigure, Perspective

# Globals and constants variables.

class PerspectiveToolbar(QtWidgets.QToolBar):

    perspectiveChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Actions
        self.group = QtWidgets.QActionGroup(self)

        for perspective in Perspective:
            action = QtWidgets.QAction(perspective.value.upper())
            action.setData(perspective)
            action.setCheckable(True)

            self.group.addAction(action)
            self.addAction(action)

        # Signals
        self.actionTriggered.connect(self._on_triggered)

    def _on_triggered(self, action):
        self.perspectiveChanged.emit(action.data())

    def perspective(self):
        return self.group.checkedAction().data()

    def setPerspective(self, perspective):
        for action in self.group.actions():
            if action.data() == perspective:
                action.setChecked(True)
                return

class SampleFigureWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        figure = Figure((6, 6))

        self.ax = figure.add_axes([0.0, 0.0, 1.0, 1.0])
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)

        self.sample_figure = SampleFigure()

        # Widgets
        self.canvas = FigureCanvas(figure)

        self.toolbar = PerspectiveToolbar()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar, 0, QtCore.Qt.AlignRight)
        self.setLayout(layout)

        # Signals
        self.toolbar.perspectiveChanged.connect(self._on_perspective_changed)

        # Defaults
        self.setPerspective(Perspective.XZ)

    def _on_perspective_changed(self, perspective):
        self.sample_figure.perspective = perspective
        self.draw()

    def draw(self):
        self.ax.clear()

        self.sample_figure.draw(self.ax)

        scalebar = ScaleBar(1.0, location='lower left')
        self.ax.add_artist(scalebar)

        self.canvas.draw()

    def clear(self):
        self.sample_figure.sample = None
        self.sample_figure.beams.clear()
        self.sample_figure.trajectories.clear()
        self.draw()

    def setSample(self, sample):
        self.sample_figure.sample = sample
        self.draw()

    def addBeam(self, beam):
        self.sample_figure.beams.append(beam)
        self.draw()

    def perspective(self):
        return self.toolbar.perspective()

    def setPerspective(self, perspective):
        self.toolbar.setPerspective(perspective)
        self.draw()

def run(): #pragma: no cover
    import sys
    from pymontecarlo.options.beam import GaussianBeam
    from pymontecarlo.options.sample import HorizontalLayerSample
    from pymontecarlo.options.material import Material

    app = QtWidgets.QApplication(sys.argv)

    widget = SampleFigureWidget()

    sample = HorizontalLayerSample(Material.pure(29))
    sample.add_layer(Material.pure(30), 10e-9)
    widget.setSample(sample)

    beam = GaussianBeam(15e3, 5e-9)
    widget.addBeam(beam)

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
