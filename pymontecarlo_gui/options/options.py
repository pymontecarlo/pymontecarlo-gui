""""""

# Standard library modules.
import contextlib

# Third party modules.
from qtpy import QtCore, QtGui, QtWebEngineWidgets

# Local modules.
from pymontecarlo.formats.document import publish_html, DocumentBuilder
from pymontecarlo.options.options import Options, OptionsBuilder
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.material import Material
from pymontecarlo.mock import ProgramMock

from pymontecarlo_gui.project import SettingsBasedField

# Globals and constants variables.


@contextlib.contextmanager
def estimated_builder(builder):
    program_mock_added = False
    if not builder.programs:
        builder.add_program(ProgramMock())
        program_mock_added = True

    beam_mock_added = False
    if not builder.beams:
        builder.add_beam(PencilBeam(10e3))
        beam_mock_added = True

    sample_mock_added = False
    if not builder.samples:
        builder.add_sample(SubstrateSample(Material.pure(26)))
        sample_mock_added = True

    try:
        yield builder

    finally:
        if program_mock_added:
            builder.programs.clear()
        if beam_mock_added:
            builder.beams.clear()
        if sample_mock_added:
            builder.samples.clear()


class OptionsModel(QtCore.QObject):

    beamsChanged = QtCore.Signal()
    samplesChanged = QtCore.Signal()
    analysesChanged = QtCore.Signal()
    programsChanged = QtCore.Signal()
    optionsChanged = QtCore.Signal()

    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.builder = OptionsBuilder()
        self._list_options = []
        self._estimated = False

    def setSamples(self, samples):
        if self.builder.samples == samples:
            return

        self.builder.samples.clear()
        self.builder.samples.extend(samples)
        # self._calculate()
        self.samplesChanged.emit()
        self.optionsChanged.emit()

    def setBeams(self, beams):
        if self.builder.beams == beams:
            return

        self.builder.beams.clear()
        self.builder.beams.extend(beams)
        # self._calculate()
        self.beamsChanged.emit()
        self.optionsChanged.emit()

    def setAnalyses(self, analyses):
        if self.builder.analyses == analyses:
            return

        self.builder.analyses.clear()
        self.builder.analyses.extend(analyses)
        # self._calculate()
        self.analysesChanged.emit()
        self.optionsChanged.emit()

    def setPrograms(self, programs):
        if self.builder.programs == programs:
            return

        self.builder.programs.clear()
        self.builder.programs.extend(programs)
        # self._calculate()
        self.programsChanged.emit()
        self.optionsChanged.emit()

    def optionsList(self):
        return self.builder.build()

    def iterOptions(self):
        yield from self.builder.iterbuild()

    def optionsCount(self):
        with estimated_builder(self.builder):
            return len(self.builder)


class OptionsField(SettingsBasedField):
    def __init__(self, options, settings):
        super().__init__(settings)

        self._options = options
        self._widget = None

        # Signals
        settings.settings_changed.connect(self._on_settings_changed)

    def _on_settings_changed(self):
        if self._widget is not None:
            self._widget.setHtml(self._render_html())

    def _render_html(self):
        builder = DocumentBuilder(self.settings())
        self.options().convert_document(builder)

        return publish_html(builder).decode("utf8")

    def _create_widget(self):
        widget = QtWebEngineWidgets.QWebEngineView()
        widget.setHtml(self._render_html())
        return widget

    def title(self):
        return "Options"

    def icon(self):
        return QtGui.QIcon.fromTheme("document-properties")

    def widget(self):
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def options(self):
        return self._options
