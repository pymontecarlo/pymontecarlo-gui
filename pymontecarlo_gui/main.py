""""""

# Standard library modules.
import os
import functools
import multiprocessing
import asyncio
import concurrent.futures
import logging
logger = logging.getLogger(__name__)

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo.settings import Settings
from pymontecarlo.project import Project
from pymontecarlo.formats.hdf5.reader import HDF5Reader
from pymontecarlo.formats.hdf5.writer import HDF5Writer
from pymontecarlo.runner.local import LocalSimulationRunner
from pymontecarlo.util.entrypoint import resolve_entrypoints
from pymontecarlo.util.token import TokenState

from pymontecarlo_gui.project import \
    (ProjectField, ProjectSummaryTableField, ProjectSummaryFigureField,
     SimulationsField, SimulationField, ResultsField)
from pymontecarlo_gui.options.options import OptionsField
from pymontecarlo_gui.widgets.field import FieldTree, FieldMdiArea, ExceptionField
from pymontecarlo_gui.widgets.future import \
    FutureThread, FutureTableWidget, ExecutorCancelThread
from pymontecarlo_gui.widgets.icon import load_icon
from pymontecarlo_gui.newsimulation import NewSimulationWizard
from pymontecarlo_gui.settings import SettingsDialog
from pymontecarlo_gui.util.entrypoint import ENTRYPOINT_GUI_PROGRAMS

# Globals and constants variables.

def has_programs():
    return bool(resolve_entrypoints(ENTRYPOINT_GUI_PROGRAMS))

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, loop, parent=None):
        super().__init__(parent)
        self.setWindowTitle('pyMonteCarlo')

        # Variables
        self._loop = loop

        self._dirpath_open = None
        self._dirpath_save = None
        self._should_save = False

        self._project = Project()

        self._settings = Settings.read()

        self._reader = HDF5Reader()
        self._reader.start()

        self._writer = HDF5Writer()
        self._writer.start()

        max_workers = multiprocessing.cpu_count() - 1
        self._runner = LocalSimulationRunner(self._project, max_workers=max_workers)

        # Actions
        self.action_new_project = QtWidgets.QAction('New project')
        self.action_new_project.setIcon(QtGui.QIcon.fromTheme('document-new'))
        self.action_new_project.setShortcut(QtGui.QKeySequence.New)
        self.action_new_project.triggered.connect(self.newProject)

        self.action_open_project = QtWidgets.QAction('Open project')
        self.action_open_project.setIcon(QtGui.QIcon.fromTheme('document-open'))
        self.action_open_project.setShortcut(QtGui.QKeySequence.Open)
        self.action_open_project.triggered.connect(functools.partial(self.openProject, None))

        self.action_save_project = QtWidgets.QAction('Save project')
        self.action_save_project.setIcon(QtGui.QIcon.fromTheme('document-save'))
        self.action_save_project.setShortcut(QtGui.QKeySequence.Save)
        self.action_save_project.triggered.connect(functools.partial(self.saveProject, None))

        self.action_settings = QtWidgets.QAction('Settings')
        self.action_settings.setIcon(QtGui.QIcon.fromTheme('preferences-system'))
        self.action_settings.setShortcut(QtGui.QKeySequence.Preferences)
        self.action_settings.triggered.connect(self._on_settings)

        self.action_quit = QtWidgets.QAction('Quit')
        self.action_quit.setShortcut(QtGui.QKeySequence.Quit)
        self.action_quit.triggered.connect(self.close)

        self.action_create_simulations = QtWidgets.QAction('Create new simulations')
        self.action_create_simulations.setIcon(load_icon('newsimulation.svg'))
        self.action_create_simulations.triggered.connect(self._on_create_new_simulations)

        self.action_stop_simulations = QtWidgets.QAction('Stop all simulations')
        self.action_stop_simulations.setIcon(QtGui.QIcon.fromTheme('media-playback-stop'))
        self.action_stop_simulations.triggered.connect(self._on_stop_all_simulations)
        self.action_stop_simulations.setEnabled(False)

        # Timers
        self.timer_runner = QtCore.QTimer()
        self.timer_runner.setInterval(1000)
        self.timer_runner.setSingleShot(False)

        # Menus
        menu = self.menuBar()
        menu_file = menu.addMenu('File')
        menu_file.addAction(self.action_new_project)
        menu_file.addAction(self.action_open_project)
        menu_file.addAction(self.action_save_project)
        menu_file.addSeparator()
        menu_file.addAction(self.action_settings)
        menu_file.addSeparator()
        menu_file.addAction(self.action_quit)

        menu_simulation = menu.addMenu('Simulation')
        menu_simulation.addAction(self.action_create_simulations)
        menu_simulation.addAction(self.action_stop_simulations)

        # Tool bar
        toolbar_file = self.addToolBar("File")
        toolbar_file.addAction(self.action_new_project)
        toolbar_file.addAction(self.action_open_project)
        toolbar_file.addAction(self.action_save_project)

        toolbar_simulation = self.addToolBar("Simulation")
        toolbar_simulation.addAction(self.action_create_simulations)
        toolbar_simulation.addAction(self.action_stop_simulations)

        # Status bar
        self.statusbar_submitted = QtWidgets.QLabel()
        self.statusbar_submitted.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)

        self.statusbar_done = QtWidgets.QLabel()
        self.statusbar_done.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)

        self.statusbar_progressbar = QtWidgets.QProgressBar()
        self.statusbar_progressbar.setRange(0, 100)

        statusbar = self.statusBar()
        statusbar.addPermanentWidget(self.statusbar_submitted)
        statusbar.addPermanentWidget(self.statusbar_done)
        statusbar.addPermanentWidget(self.statusbar_progressbar)

        # Widgets
        self.tree = FieldTree()

        self.dock_project = QtWidgets.QDockWidget("Project")
        self.dock_project.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                                          QtCore.Qt.RightDockWidgetArea)
        self.dock_project.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures |
                                      QtWidgets.QDockWidget.DockWidgetMovable)
        self.dock_project.setWidget(self.tree)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_project)

        self.table_runner = FutureTableWidget()
        self.table_runner.act_clear.setText('Clear done simulation(s)')

        self.dock_runner = QtWidgets.QDockWidget("Run")
        self.dock_runner.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                                         QtCore.Qt.RightDockWidgetArea)
        self.dock_runner.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures |
                                     QtWidgets.QDockWidget.DockWidgetMovable)
        self.dock_runner.setWidget(self.table_runner)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_runner)

        self.tabifyDockWidget(self.dock_project, self.dock_runner)
        self.dock_project.raise_()

        self.mdiarea = FieldMdiArea()

        self.setCentralWidget(self.mdiarea)

        # Dialogs
        self.wizard_simulation = NewSimulationWizard()

        self.dialog_settings = SettingsDialog()

        # Signals
#        self._runner.submitted.connect(self._on_future_submitted)

        self.tree.doubleClicked.connect(self._on_tree_double_clicked)

        self.mdiarea.windowOpened.connect(self._on_mdiarea_window_opened)
        self.mdiarea.windowClosed.connect(self._on_mdiarea_window_closed)

        self.timer_runner.timeout.connect(self._on_timer_runner_timeout)

        self.table_runner.doubleClicked.connect(self._on_table_runner_double_clicked)

        # Defaults
        self.setProject(self._project)

        asyncio.run_coroutine_threadsafe(self._runner.start(), loop)

        self.timer_runner.start()

    def _on_tree_double_clicked(self, field):
        if field.widget().children():
            self.mdiarea.addField(field)

    def _on_mdiarea_window_opened(self, field):
        if not self.tree.containField(field):
            return
        font = self.tree.fieldFont(field)
        font.setUnderline(True)
        self.tree.setFieldFont(field, font)

    def _on_mdiarea_window_closed(self, field):
        if not self.tree.containField(field):
            return
        font = self.tree.fieldFont(field)
        font.setUnderline(False)
        self.tree.setFieldFont(field, font)

    def _on_timer_runner_timeout(self):
        token = self._runner.token
        subtokens = token.subtokens

        progress = int(token.progress * 100)
        self.statusbar_progressbar.setValue(progress)

        status = token.status
        timeout = self.timer_runner.interval()
        self.statusBar().showMessage(status, timeout)

        submitted_count = len(subtokens)
        if submitted_count == 0:
            text = 'No simulation submitted'
        elif submitted_count == 1:
            text = '1 simulation submitted'
        else:
            text = '{} simulations submitted'.format(submitted_count)
        self.statusbar_submitted.setText(text)

        done_count = sum(subtoken.state == TokenState.DONE
                         for subtoken in subtokens)
        if done_count == 0:
            text = 'No simulation done'
        elif done_count == 1:
            text = '1 simulation done'
        else:
            text = '{} simulations done'.format(done_count)
        self.statusbar_done.setText(text)

        is_running = token.state == TokenState.RUNNING
        self.action_stop_simulations.setEnabled(is_running)

    def _on_future_submitted(self, future):
        self.table_runner.addFuture(future)

    def _on_table_runner_double_clicked(self, future):
        if not future.done():
            return

        if future.cancelled():
            return

        if not future.exception():
            return

        field = ExceptionField(future.exception())
        self.mdiarea.addField(field)

    def _on_create_new_simulations(self):
        if not has_programs():
            title = 'New simulations'
            message = 'No program is activated. ' + \
                'Go to File > Settings to activate at least one program.'
            QtWidgets.QMessageBox.critical(self, title, message)
            return

        self.wizard_simulation.restart()
        if not self.wizard_simulation.exec_():
            return

        list_options = self.wizard_simulation.optionsList()
        logger.debug('Wizard defined {} simulations'.format(len(list_options)))

        asyncio.run_coroutine_threadsafe(self._runner.submit(*list_options), self._loop)

        logger.debug('Submitted simulations')

        self.dock_runner.raise_()

    def _on_stop_all_simulations(self):
        dialog = QtWidgets.QProgressDialog()
        dialog.setWindowTitle('Stop')
        dialog.setLabelText('Stopping all simulations')
        dialog.setMinimum(0)
        dialog.setMaximum(0)
        dialog.setValue(0)
        dialog.setCancelButton(None)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)

        thread = ExecutorCancelThread(self._runner)
        thread.finished.connect(dialog.close)

        thread.start()
        dialog.exec_()

    def _on_settings(self):
        self.dialog_settings.setSettings(self._settings)

        if not self.dialog_settings.exec_():
            return

        self.dialog_settings.updateSettings(self._settings)
        self._settings.settings_changed.send()

    def _run_future_in_thread(self, future, title):
        dialog = QtWidgets.QProgressDialog()
        dialog.setWindowTitle(title)
        dialog.setRange(0, 100)

        thread = FutureThread(future)
        thread.progressChanged.connect(dialog.setValue)
        thread.statusChanged.connect(dialog.setLabelText)
        thread.finished.connect(dialog.close)

        thread.start()
        dialog.exec_()

    def _check_save(self):
        if not self.shouldSave():
            return True

        caption = 'Save current project'
        message = 'Would you like to save the current project?'
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        answer = QtWidgets.QMessageBox.question(None, caption, message, buttons)

        if answer == QtWidgets.QMessageBox.Yes:
            return self.saveProject()

        return True

    def closeEvent(self, event):
        state = self._runner.token.state
        if state == TokenState.RUNNING:
            caption = 'Quit'
            message = 'One or more simulations are running. Do you really want to quit?'
            buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            answer = QtWidgets.QMessageBox.question(None, caption, message, buttons)

            if answer == QtWidgets.QMessageBox.No:
                event.reject()
                return

        futures = []
        futures.append(asyncio.run_coroutine_threadsafe(self._runner.cancel(), self._loop))
        futures.append(asyncio.run_coroutine_threadsafe(self._runner.shutdown(), self._loop))

        concurrent.futures.wait(futures)

        event.accept()

    def openPath(self):
        if self._dirpath_open is None:
            if self._dirpath_save is None:
                self._dirpath_open = os.getcwd()
            else:
                self._dirpath_open = self._dirpath_save
        return self._dirpath_open

    def savePath(self):
        if self._dirpath_save is None:
            if self._dirpath_save is None:
                self._dirpath_open = os.getcwd()
            else:
                self._dirpath_save = self._dirpath_open
        return self._dirpath_save

    def project(self):
        return self._project

    def setProject(self, project):
        if self._project is not None:
            self._project.simulation_added.disconnect(self.addSimulation)

        self._project = project
        self._project.simulation_added.connect(self.addSimulation)
#        self._runner.project = project

        if project.filepath:
            self._dirpath_open = os.path.dirname(project.filepath)

        self.mdiarea.clear()
        self.tree.clear()
#        self._runner.submitted_options.clear()

        field_project = ProjectField(self._settings, project)
        self.tree.addField(field_project)

        for index, simulation in enumerate(project.simulations, 1):
            self.addSimulation(simulation, index)

        self.tree.expandField(field_project)

        self.setShouldSave(False)

    def newProject(self):
        if not self._check_save():
            return False

        self.setProject(Project())

        self.dock_project.raise_()
        return True

    def openProject(self, filepath=None):
#        if self._runner.running():
#            caption = 'Open project'
#            message = 'Simulations are running. New project cannot be opened.'
#            QtWidgets.QMessageBox.critical(None, caption, message)
#            return False

        if not self._check_save():
            return False

        if filepath is None:
            caption = 'Open project'
            dirpath = self.openPath()
            namefilters = 'Simulation project (*.mcsim)'
            filepath, namefilter = \
                QtWidgets.QFileDialog.getOpenFileName(None, caption, dirpath, namefilters)

            if not namefilter:
                return False

            if not filepath:
                return False

        future = self._reader.submit(filepath)
        self._run_future_in_thread(future, 'Open project')

        project = future.result()
        self.setProject(project)

        self.dock_project.raise_()
        return True

    def saveProject(self, filepath=None):
        if filepath is None:
            filepath = self._project.filepath

        if filepath is None:
            caption = 'Save project'
            dirpath = self.savePath()
            namefilters = 'Simulation project (*.mcsim)'
            filepath, namefilter = \
                QtWidgets.QFileDialog.getSaveFileName(None, caption, dirpath, namefilters)

            if not namefilter:
                return False

            if not filepath:
                return False

        if not filepath.endswith('.mcsim'):
            filepath += '.mcsim'

        future = self._writer.submit(self._project, filepath)
        self._run_future_in_thread(future, 'Save project')

        self._project.filepath = filepath
        self._dirpath_save = os.path.dirname(filepath)

        caption = 'Save project'
        message = 'Project saved'
        QtWidgets.QMessageBox.information(None, caption, message)

        self.setShouldSave(False)

        return True

    def addSimulation(self, simulation, index=None):
        def _find_field(field_project, clasz):
            children = self.tree.childrenField(field_project)

            for field in children:
                if isinstance(field, clasz):
                    return field

            return None

        toplevelfields = self.tree.topLevelFields()
        assert len(toplevelfields) == 1

        field_project = toplevelfields[0]
        settings = self._settings
        project = field_project.project()

        # Summary table
        field_summary_table = _find_field(field_project, ProjectSummaryTableField)
        if not field_summary_table:
            field_summary_table = ProjectSummaryTableField(settings, project)
            self.tree.addField(field_summary_table, field_project)

        field_summary_table.setProject(project)

        # Summary figure
        field_summary_figure = _find_field(field_project, ProjectSummaryFigureField)
        if not field_summary_figure:
            field_summary_figure = ProjectSummaryFigureField(settings, project)
            self.tree.addField(field_summary_figure, field_project)

        field_summary_figure.setProject(project)

        # Simulations
        field_simulations = _find_field(field_project, SimulationsField)
        if not field_simulations:
            field_simulations = SimulationsField()
            self.tree.addField(field_simulations, field_project)

        # Simulation
        if index is None:
            index = project.simulations.index(simulation) + 1
        field_simulation = SimulationField(index, simulation)
        self.tree.addField(field_simulation, field_simulations)

        field_options = OptionsField(simulation.options, self._settings)
        self.tree.addField(field_options, field_simulation)

        if not simulation.results:
            return

        field_results = ResultsField()
        self.tree.addField(field_results, field_simulation)

        self.tree.tree.reset()
        self.tree.expandField(field_project)
        self.tree.expandField(field_simulations)

        self.setShouldSave(True)

    def shouldSave(self):
        return self._should_save

    def setShouldSave(self, should_save):
        toplevelfields = self.tree.topLevelFields()
        assert len(toplevelfields) == 1

        field_project = toplevelfields[0]
        font = self.tree.fieldFont(field_project)
        font.setItalic(should_save)
        self.tree.setFieldFont(field_project, font)

        self._should_save = should_save


