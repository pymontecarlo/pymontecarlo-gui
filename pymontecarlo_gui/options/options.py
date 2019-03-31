""""""

# Standard library modules.

# Third party modules.
from qtpy import QtGui, QtWebEngineWidgets

# Local modules.
from pymontecarlo.formats.document import publish_html, DocumentBuilder

from pymontecarlo_gui.project import _SettingsBasedField

# Globals and constants variables.

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
