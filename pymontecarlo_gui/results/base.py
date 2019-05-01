""""""

# Standard library modules.
import csv
import functools

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

# Local modules.
from pymontecarlo_gui.settings import SettingsBasedField
from pymontecarlo_gui.widgets.dialog import ExecutionProgressDialog

from pymontecarlo.formats.document import publish_html, DocumentBuilder

# Globals and constants variables.

class ResultWidgetBase(QtWidgets.QWidget):

    def __init__(self, result, settings, parent=None):
        super().__init__(parent)

        # Variables
        self._result = result
        self._settings = settings

    def result(self):
        return self._result

    def settings(self):
        return self._settings

class ResultTableWidgetBase(ResultWidgetBase):

    def __init__(self, result, settings, parent=None):
        super().__init__(result, settings, parent)

        # Actions
        self.action_copy = QtWidgets.QAction('Copy to clipboard')
        self.action_copy.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        self.action_copy.setShortcut(QtGui.QKeySequence.Copy)
        self.action_copy.triggered.connect(self._on_copy)

        self.action_save = QtWidgets.QAction('Save')
        self.action_save.setIcon(QtGui.QIcon.fromTheme('document-save'))
        self.action_save.triggered.connect(self._on_save)

        # Widgets
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self._create_model(result, settings))
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.web_widget = QtWebEngineWidgets.QWebEngineView()
        self.web_widget.setHtml(self._render_html(result, settings))

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addAction(self.action_copy)
        self.toolbar.addAction(self.action_save)

        # Layouts
        widget = QtWidgets.QTabWidget()
        widget.addTab(self.table_view, 'Results')
        widget.addTab(self.web_widget, 'Analysis')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(widget)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)

        # Signals
        settings.settings_changed.connect(self._on_settings_changed)

    def _create_model(self, result, settings):
        raise NotImplementedError

    def _render_html(self, result, settings):
        builder = DocumentBuilder(settings)
        result.analysis.convert_document(builder)
        return publish_html(builder).decode('utf8')

    def _on_settings_changed(self):
        model = self.table_view.model()
        model.modelReset.emit()

    def _get_data(self):
        model = self.table_view.model()

        rows = []

        # Header
        header = []

        for icol in range(model.columnCount()):
            header.append(model.headerData(icol, QtCore.Qt.Horizontal, QtCore.Qt.UserRole))

        rows.append(header)

        # Data
        for irow in range(model.rowCount()):
            row = []

            for icol in range(model.columnCount()):
                index = model.createIndex(irow, icol)
                row.append(model.data(index, QtCore.Qt.UserRole))

            rows.append(row)

        return rows

    def _on_copy(self):
        data = self._get_data()
        print(data)

    def _save_data(self, filepath):
        data = self._get_data()

        with open(filepath, 'w') as fp:
            writer = csv.writer(fp, lineterminator='\n')
            writer.writerows(data)

    def _on_save(self):
        caption = 'Save result'
        dirpath = self.settings().savedir
        namefilters = 'CSV text file (*.csv) || Excel spreadsheet (*.xlsx)'
        filepath, namefilter = \
            QtWidgets.QFileDialog.getSaveFileName(self, caption, dirpath, namefilters)

        if not namefilter:
            return False

        if not filepath:
            return False

        if not filepath.endswith('.csv'):
            filepath += '.csv'

        function = functools.partial(self._save_data, filepath)
        dialog = ExecutionProgressDialog('Save result', 'Saving result...', 'Result saved', function)
        dialog.exec_()

class ResultSummaryWidgetBase(QtWidgets.QWidget):

    def setProject(self, project):
        raise NotImplementedError

class ResultFieldBase(SettingsBasedField):

    def __init__(self, result, settings):
        self._result = result
        super().__init__(settings)

    def title(self):
        return self.result().getname()

    def icon(self):
        return QtGui.QIcon.fromTheme('format-justify-fill')

    def result(self):
        return self._result
