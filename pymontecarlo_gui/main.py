""""""

# Standard library modules.
import os
import functools
import multiprocessing

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
import pymontecarlo
from pymontecarlo.project import Project
from pymontecarlo.fileformat.reader import HDF5Reader
from pymontecarlo.fileformat.writer import HDF5Writer
from pymontecarlo.runner.local import LocalSimulationRunner

from pymontecarlo_gui.project import \
    (ProjectField, SimulationsField, SimulationField, OptionsField,
     ResultsField)
from pymontecarlo_gui.widgets.field import FieldTree, FieldMdiArea, ExceptionField
from pymontecarlo_gui.widgets.future import \
    FutureThread, FutureTableWidget, ExecutorCancelThread
from pymontecarlo_gui.widgets.icon import load_icon
from pymontecarlo_gui.newsimulation import NewSimulationWizard

# Globals and constants variables.

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('pyMonteCarlo')

        # Variables
        self._settings = pymontecarlo.settings

        self._dirpath_open = None
        self._dirpath_save = None
        self._should_save = False

        self._project = Project()

        self._reader = HDF5Reader()
        self._reader.start()

        self._writer = HDF5Writer()
        self._writer.start()

        maxworkers = 1 #multiprocessing.cpu_count() - 1
        self._runner = LocalSimulationRunner(self._project, maxworkers)
        self._runner.start()

        # Actions
        self.action_new_project = QtWidgets.QAction('New project')
        self.action_new_project.setIcon(QtGui.QIcon.fromTheme('document-new'))
        self.action_new_project.triggered.connect(self.newProject)

        self.action_open_project = QtWidgets.QAction('Open project')
        self.action_open_project.setIcon(QtGui.QIcon.fromTheme('document-open'))
        self.action_open_project.triggered.connect(functools.partial(self.openProject, None))

        self.action_save_project = QtWidgets.QAction('Save project')
        self.action_save_project.setIcon(QtGui.QIcon.fromTheme('document-save'))
        self.action_save_project.triggered.connect(functools.partial(self.saveProject, None))

        self.action_create_simulations = QtWidgets.QAction('Create new simulations')
        self.action_create_simulations.setIcon(load_icon('newsimulation.svg'))
        self.action_create_simulations.triggered.connect(self.showNewSimulationsWizard)

        self.action_stop_simulations = QtWidgets.QAction('Stop all simulations')
        self.action_stop_simulations.setIcon(QtGui.QIcon.fromTheme('media-playback-stop'))
        self.action_stop_simulations.triggered.connect(self.stopAllSimulations)
        self.action_stop_simulations.setEnabled(False)

        self.action_submit = QtWidgets.QAction('Submit')
        self.action_submit.triggered.connect(self._on_submit)

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

        menu_simulation = menu.addMenu('Simulation')
        menu_simulation.addAction(self.action_create_simulations)
        menu_simulation.addAction(self.action_stop_simulations)

        # Tool bar
        toolbar_file = self.addToolBar("File")
        toolbar_file.addAction(self.action_new_project)
        toolbar_file.addAction(self.action_open_project)
        toolbar_file.addAction(self.action_save_project)
        toolbar_file.addAction(self.action_submit)

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

        # Signals
        self.tree.doubleClicked.connect(self._on_tree_double_clicked)

        self.mdiarea.windowOpened.connect(self._on_mdiarea_window_opened)
        self.mdiarea.windowClosed.connect(self._on_mdiarea_window_closed)

        self.timer_runner.timeout.connect(self._on_timer_runner_timeout)

        self.table_runner.doubleClicked.connect(self._on_table_runner_double_clicked)

        # Defaults
        self.setProject(self._project)

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
        progress = int(self._runner.progress * 100)
        self.statusbar_progressbar.setValue(progress)

        status = self._runner.status
        timeout = self.timer_runner.interval()
        self.statusBar().showMessage(status, timeout)

        submitted_count = self._runner.submitted_count
        if submitted_count == 0:
            text = 'No simulation submitted'
        elif submitted_count == 1:
            text = '1 simulation submitted'
        else:
            text = '{} simulations submitted'.format(submitted_count)
        self.statusbar_submitted.setText(text)

        done_count = self._runner.done_count
        if done_count == 0:
            text = 'No simulation done'
        elif done_count == 1:
            text = '1 simulation done'
        else:
            text = '{} simulations done'.format(done_count)
        self.statusbar_done.setText(text)

        self.action_stop_simulations.setEnabled(self._runner.running())

    def _on_submit(self):
        import math
        from pymontecarlo.options.beam import GaussianBeam
        from pymontecarlo.options.material import Material
        from pymontecarlo.options.sample import SubstrateSample
        from pymontecarlo.options.detector import PhotonDetector
        from pymontecarlo.options.analysis import KRatioAnalysis
        from pymontecarlo.options.limit import ShowersLimit
        from pymontecarlo.options.options import Options

        program = pymontecarlo.settings.get_program('casino2')
        beam = GaussianBeam(15e3, 10e-9)
        mat1 = Material.pure(29)
        sample = SubstrateSample(mat1)

        photon_detector = PhotonDetector(math.radians(35.0))
        analysis = KRatioAnalysis(photon_detector)

        limit = ShowersLimit(10000)

        options = Options(program, beam, sample, [analysis], [limit])
        futures = self._runner.submit(options)

        for future in futures:
            future.add_done_callback(self._on_simulation_done)
            self.table_runner.addFuture(future)

        self.dock_runner.raise_()

    def _on_simulation_done(self, future):
        if future.cancelled():
            return

        if future.exception():
            return

        self.addSimulation(future.result())
        self.setShouldSave(True)

    def _on_table_runner_double_clicked(self, future):
        if not future.done():
            return

        if future.cancelled():
            return

        if not future.exception():
            return

        field = ExceptionField(future.exception())
        self.mdiarea.addField(field)

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

    def settings(self):
        return self._settings

    def project(self):
        return self._project

    def setProject(self, project):
        self._project = project
        self._runner.project = project

        if project.filepath:
            self._dirpath_open = os.path.dirname(project.filepath)

        self.mdiarea.clear()
        self.tree.clear()
        self._runner.submitted_options.clear()

        field_project = ProjectField()
        self.tree.addField(field_project)

        for simulation in project.simulations:
            self.addSimulation(simulation)

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

    def addSimulation(self, simulation):
        toplevelfields = self.tree.topLevelFields()
        assert len(toplevelfields) == 1

        field_project = toplevelfields[0]

        has_simulations_field = False
        children = self.tree.childrenField(field_project)

        for field in children:
            if isinstance(field, SimulationsField):
                has_simulations_field = True
                field_simulations = field
                break

        if not has_simulations_field:
            field_simulations = SimulationsField()
            self.tree.addField(field_simulations, field_project)

        field_simulation = SimulationField()
        self.tree.addField(field_simulation, field_simulations)

        field_options = OptionsField()
        field_options.setOptions(simulation.options)
        self.tree.addField(field_options, field_simulation)

        if not simulation.results:
            return

        field_results = ResultsField()
        self.tree.addField(field_results, field_simulation)

        self.tree.tree.reset()
        self.tree.expandField(field_project)
        self.tree.expandField(field_simulations)

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

    def showNewSimulationsWizard(self):
        wizard = NewSimulationWizard()

        if not wizard.exec_():
            return

        for options in wizard.optionsList():
            futures = self._runner.submit(options)

            for future in futures:
                future.add_done_callback(self._on_simulation_done)
                self.table_runner.addFuture(future)

        self.dock_runner.raise_()

    def stopAllSimulations(self):
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
