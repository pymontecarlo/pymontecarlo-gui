""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtGui, QtWebEngineWidgets

# Local modules.
from pymontecarlo.formats.document import publish_html, DocumentBuilder
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.mock import ProgramMock

from pymontecarlo_gui.project import _SettingsBasedField

# Globals and constants variables.

class OptionsModel(QtCore.QObject):

    optionsChanged = QtCore.Signal()

    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.builder = OptionsBuilder()
        self._list_options = []
        self._estimated = False

    def _calculate(self):
        program_mock_added = False
        if not self.builder.programs:
            self.builder.add_program(ProgramMock())
            program_mock_added = True

        beam_mock_added = False
        if not self.builder.beams:
            self.builder.add_beam(None) #TODO: Change back
            beam_mock_added = True

        sample_mock_added = False
        if not self.builder.samples:
            self.builder.add_sample(None)
            sample_mock_added = True

        if program_mock_added and beam_mock_added and sample_mock_added:
            list_options = []
        else:
            list_options = self.builder.build()

        if program_mock_added:
            self.builder.programs.clear()
        if beam_mock_added:
            self.builder.beams.clear()
        if sample_mock_added:
            self.builder.samples.clear()

        self._estimated = program_mock_added or beam_mock_added or sample_mock_added
        self._list_options = tuple(list_options)

    def setSamples(self, samples):
        if self.builder.samples == samples:
            return

        self.builder.samples.clear()
        self.builder.samples.extend(samples)
        self._calculate()
        self.optionsChanged.emit()

    def setBeams(self, beams):
        self.builder.beams.clear()
        self.builder.beams.extend(beams)
        self._calculate()
        self.optionsChanged.emit()

    def setAnalyses(self, analyses):
        self.builder.analyses.clear()
        self.builder.analyses.extend(analyses)
        self._calculate()
        self.optionsChanged.emit()

    def setPrograms(self, programs):
        self.builder.programs.clear()
        self.builder.programs.extend(programs)
        self._calculate()
        self.optionsChanged.emit()

    def isOptionListEstimated(self):
        return self._estimated

    def getOptionsList(self, estimate=False):
        if self.isOptionListEstimated() and not estimate:
            return []
        return self._list_options

class OptionsField(_SettingsBasedField):

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

        return publish_html(builder).decode('utf8')

    def _create_widget(self):
        widget = QtWebEngineWidgets.QWebEngineView()
        widget.setHtml(self._render_html())
        return widget

    def title(self):
        return 'Options'

    def icon(self):
        return QtGui.QIcon.fromTheme('document-properties')

    def widget(self):
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def options(self):
        return self._options
