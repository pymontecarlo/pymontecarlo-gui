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
from pymontecarlo_gui.widgets.future import FutureThread, FutureTableWidget

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
        self.action_open_project = QtWidgets.QAction('Open project')
        self.action_open_project.setIcon(QtGui.QIcon.fromTheme('document-open'))
        self.action_open_project.triggered.connect(functools.partial(self.openProject, None))

        self.action_submit = QtWidgets.QAction('Submit')
        self.action_submit.triggered.connect(self._on_submit)

        # Timers
        self.timer_runner = QtCore.QTimer()
        self.timer_runner.setInterval(1000)
        self.timer_runner.setSingleShot(False)

        # Menus
        menu = self.menuBar()
        menu_file = menu.addMenu('File')
        menu_file.addAction(self.action_open_project)

        # Tool bar
        toolbar = self.addToolBar("main")
        toolbar.setMovable(False)
        toolbar.addAction(self.action_open_project)
        toolbar.addAction(self.action_submit)

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

        self.dock_queue = QtWidgets.QDockWidget("Run")
        self.dock_queue.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                                        QtCore.Qt.RightDockWidgetArea)
        self.dock_queue.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures |
                                    QtWidgets.QDockWidget.DockWidgetMovable)
        self.dock_queue.setWidget(self.table_runner)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_queue)

        self.tabifyDockWidget(self.dock_project, self.dock_queue)
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
        self._update_project(self._project)

        self.timer_runner.start()

    def _on_tree_double_clicked(self, field):
        if field.widget().children():
            self.mdiarea.addField(field)

    def _on_mdiarea_window_opened(self, field):
        font = self.tree.fieldFont(field)
        if font is None:
            return
        font.setUnderline(True)
        self.tree.setFieldFont(field, font)

    def _on_mdiarea_window_closed(self, field):
        font = self.tree.fieldFont(field)
        if font is None:
            return
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

        self.dock_queue.raise_()

    def _on_simulation_done(self, future):
        print('done')

    def _on_table_runner_double_clicked(self, future):
        if not future.done():
            return

        if not future.exception():
            return

        field = ExceptionField(future.exception())
        self.mdiarea.addField(field)

    def _update_project(self, project):
        self.mdiarea.clear()
        self.tree.clear()

        field_project = ProjectField()
        self.tree.addField(field_project)

        if not project.simulations:
            return

        field_simulations = SimulationsField()
        self.tree.addField(field_simulations, field_project)

        for simulation in project.simulations:
            field_simulation = SimulationField()
            self.tree.addField(field_simulation, field_simulations)

            field_options = OptionsField()
            field_options.setOptions(simulation.options)
            self.tree.addField(field_options, field_simulation)

            if not simulation.results:
                continue

            field_results = ResultsField()
            self.tree.addField(field_results, field_simulation)

        self.tree.expandField(field_project)
        self.tree.expandField(field_simulations)

    def _run_future_in_thread(self, future):
        dialog = QtWidgets.QProgressDialog()
        dialog.setWindowTitle('Open project')
        dialog.setRange(0, 100)

        thread = FutureThread(future)
        thread.progressChanged.connect(dialog.setValue)
        thread.statusChanged.connect(dialog.setLabelText)
        thread.finished.connect(dialog.close)

        thread.start()
        dialog.exec_()

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

    def openProject(self, filepath=None):
#        if self._runner.running():
#            caption = 'Open project'
#            message = 'Simulations are running. New project cannot be opened.'
#            QtWidgets.QMessageBox.critical(None, caption, message)
#            return False

        if self._should_save:
            caption = 'Save current project'
            message = 'Would you like to save the current project?'
            buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            answer = QtWidgets.QMessageBox.question(None, caption, message, buttons)

            if answer == QtWidgets.QMessageBox.Yes:
                if not self.saveProject():
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
        self._run_future_in_thread(future)

        project = future.result()
        self._update_project(project)

        self._project = project
        self._dirpath_open = os.path.dirname(project.filepath)

        self.dock_project.raise_()
        return True

