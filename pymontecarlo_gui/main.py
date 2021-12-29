""""""

# Standard library modules.
import os
import functools
import multiprocessing
import asyncio
import logging

logger = logging.getLogger(__name__)

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets
from qasync import asyncClose, asyncSlot

# Local modules.
from pymontecarlo.settings import Settings
from pymontecarlo.project import Project
from pymontecarlo.runner.local import LocalSimulationRunner
from pymontecarlo.util.token import TokenState
from pymontecarlo.results.photonintensity import PhotonIntensityResultBase
from pymontecarlo.results.kratio import KRatioResult

from pymontecarlo_gui.project import (
    ProjectField,
    ProjectSummaryTableField,
    ProjectSummaryFigureField,
    SimulationField,
)
from pymontecarlo_gui.options.options import OptionsField
from pymontecarlo_gui.options.program.base import ProgramFieldBase
from pymontecarlo_gui.results.base import ResultFieldBase
from pymontecarlo_gui.results.photonintensity import PhotonIntensityResultField
from pymontecarlo_gui.results.kratio import KRatioResultField
from pymontecarlo_gui.widgets.field import FieldTree, FieldMdiArea, ExceptionField
from pymontecarlo_gui.widgets.token import TokenTableWidget
from pymontecarlo_gui.widgets.icon import load_icon, load_pixmap
from pymontecarlo_gui.widgets.dialog import ExecutionProgressDialog
from pymontecarlo_gui.newsimulation import NewSimulationWizard
from pymontecarlo_gui.settings import SettingsDialog

# Globals and constants variables.


class MainWindow(QtWidgets.QMainWindow):

    newSimulations = QtCore.Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pyMonteCarlo")
        self.setWindowIcon(load_pixmap("logo_32x32.png"))

        # Variables
        self._should_save = False

        self._settings = Settings.read()

        max_workers = multiprocessing.cpu_count() - 1
        self._runner = LocalSimulationRunner(max_workers=max_workers)

        # Actions
        self.action_new_project = QtWidgets.QAction("New project")
        self.action_new_project.setIcon(QtGui.QIcon.fromTheme("document-new"))
        self.action_new_project.setShortcut(QtGui.QKeySequence.New)
        self.action_new_project.triggered.connect(self.newProject)

        self.action_open_project = QtWidgets.QAction("Open project")
        self.action_open_project.setIcon(QtGui.QIcon.fromTheme("document-open"))
        self.action_open_project.setShortcut(QtGui.QKeySequence.Open)
        self.action_open_project.triggered.connect(
            functools.partial(self.openProject, None)
        )

        self.action_save_project = QtWidgets.QAction("Save project")
        self.action_save_project.setIcon(QtGui.QIcon.fromTheme("document-save"))
        self.action_save_project.setShortcut(QtGui.QKeySequence.Save)
        self.action_save_project.triggered.connect(
            functools.partial(self.saveProject, None)
        )

        self.action_settings = QtWidgets.QAction("Settings")
        self.action_settings.setIcon(QtGui.QIcon.fromTheme("preferences-system"))
        self.action_settings.setShortcut(QtGui.QKeySequence.Preferences)
        self.action_settings.triggered.connect(self._on_settings)

        self.action_quit = QtWidgets.QAction("Quit")
        self.action_quit.setShortcut(QtGui.QKeySequence.Quit)
        self.action_quit.triggered.connect(self.close)

        self.action_create_simulations = QtWidgets.QAction("Create new simulations")
        self.action_create_simulations.setIcon(load_icon("newsimulation.svg"))
        self.action_create_simulations.triggered.connect(
            self._on_create_new_simulations
        )

        self.action_stop_simulations = QtWidgets.QAction("Stop all simulations")
        self.action_stop_simulations.setIcon(
            QtGui.QIcon.fromTheme("media-playback-stop")
        )
        self.action_stop_simulations.triggered.connect(self._on_stop)
        self.action_stop_simulations.setEnabled(False)

        # Timers
        self.timer_runner = QtCore.QTimer()
        self.timer_runner.setInterval(1000)
        self.timer_runner.setSingleShot(False)

        # Menus
        menu = self.menuBar()
        menu_file = menu.addMenu("File")
        menu_file.addAction(self.action_new_project)
        menu_file.addAction(self.action_open_project)
        menu_file.addAction(self.action_save_project)
        menu_file.addSeparator()
        menu_file.addAction(self.action_settings)
        menu_file.addSeparator()
        menu_file.addAction(self.action_quit)

        menu_simulation = menu.addMenu("Simulation")
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
        self.statusbar_submitted.setFrameStyle(
            QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken
        )

        self.statusbar_done = QtWidgets.QLabel()
        self.statusbar_done.setFrameStyle(
            QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken
        )

        self.statusbar_progressbar = QtWidgets.QProgressBar()
        self.statusbar_progressbar.setRange(0, 100)

        statusbar = self.statusBar()
        statusbar.addPermanentWidget(self.statusbar_submitted)
        statusbar.addPermanentWidget(self.statusbar_done)
        statusbar.addPermanentWidget(self.statusbar_progressbar)

        # Widgets
        self.tree = FieldTree()

        self.dock_project = QtWidgets.QDockWidget("Project")
        self.dock_project.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        )
        self.dock_project.setFeatures(
            QtWidgets.QDockWidget.NoDockWidgetFeatures
            | QtWidgets.QDockWidget.DockWidgetMovable
        )
        self.dock_project.setWidget(self.tree)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_project)

        self.table_runner = TokenTableWidget(self._runner.token)

        self.dock_runner = QtWidgets.QDockWidget("Run")
        self.dock_runner.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        )
        self.dock_runner.setFeatures(
            QtWidgets.QDockWidget.NoDockWidgetFeatures
            | QtWidgets.QDockWidget.DockWidgetMovable
        )
        self.dock_runner.setWidget(self.table_runner)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_runner)

        self.tabifyDockWidget(self.dock_project, self.dock_runner)
        self.dock_project.raise_()

        self.mdiarea = FieldMdiArea()

        self.setCentralWidget(self.mdiarea)

        # Dialogs
        self.wizard_simulation = NewSimulationWizard(self._settings)

        self.dialog_settings = SettingsDialog()

        # Signals
        self.tree.doubleClicked.connect(self._on_tree_double_clicked)

        self.mdiarea.windowOpened.connect(self._on_mdiarea_window_opened)
        self.mdiarea.windowClosed.connect(self._on_mdiarea_window_closed)

        self.timer_runner.timeout.connect(self._on_timer_runner_timeout)

        self.newSimulations.connect(self._on_new_simulations)

        # Start
        logger.debug("Before new project action")
        self.action_new_project.trigger()  # Required to setup project
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
        subtokens = token.get_subtokens(category="simulation")

        progress = int(token.progress * 100)
        self.statusbar_progressbar.setValue(progress)

        status = token.status
        timeout = self.timer_runner.interval()
        self.statusBar().showMessage(status, timeout)

        submitted_count = len(subtokens)
        if submitted_count == 0:
            text = "No simulation submitted"
        elif submitted_count == 1:
            text = "1 simulation submitted"
        else:
            text = "{} simulations submitted".format(submitted_count)
        self.statusbar_submitted.setText(text)

        done_count = sum(subtoken.state == TokenState.DONE for subtoken in subtokens)
        if done_count == 0:
            text = "No simulation done"
        elif done_count == 1:
            text = "1 simulation done"
        else:
            text = "{} simulations done".format(done_count)
        self.statusbar_done.setText(text)

        is_running = token.state == TokenState.RUNNING
        self.action_new_project.setEnabled(not is_running)
        self.action_open_project.setEnabled(not is_running)
        self.action_stop_simulations.setEnabled(is_running)

    def _on_create_new_simulations(self):
        if not ProgramFieldBase._subclasses:
            title = "New simulations"
            message = (
                "No program is activated. "
                + "Go to File > Settings to activate at least one program."
            )
            QtWidgets.QMessageBox.critical(self, title, message)
            return

        self.wizard_simulation.restart()
        if not self.wizard_simulation.exec_():
            return

        list_options = self.wizard_simulation.optionsList()
        logger.debug("Wizard defined {} simulation(s)".format(len(list_options)))

        self.newSimulations.emit(list_options)

    @asyncSlot()
    async def _on_new_simulations(self, list_options):
        # # Check save project
        # if self.project().filepath is None:
        #     caption = 'Save project'
        #     message = 'Would you like to save the project before running the simulation(s)?'
        #     buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        #     answer = QtWidgets.QMessageBox.question(None, caption, message, buttons)

        #     if answer == QtWidgets.QMessageBox.Yes:
        #         self.saveProject()

        # Start runner (nothing happens if already running)
        await self._runner.start()

        # Submit simulation(s)
        await self._runner.submit(*list_options)
        logger.debug("Submitted simulation(s)")

        self.dock_runner.raise_()

    @asyncSlot()
    async def _on_stop(self):
        await self._runner.cancel()

    def _on_settings(self):
        self.dialog_settings.setSettings(self.settings())

        if not self.dialog_settings.exec_():
            return

        self.dialog_settings.updateSettings(self.settings())
        self.settings().settings_changed.send()

    def _check_save(self):
        if not self.shouldSave():
            return True

        caption = "Save current project"
        message = "Would you like to save the current project?"
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        answer = QtWidgets.QMessageBox.question(None, caption, message, buttons)

        if answer == QtWidgets.QMessageBox.Yes:
            return self.saveProject()

        return True

    @asyncClose
    async def closeEvent(self, event):
        state = self._runner.token.state
        if state == TokenState.RUNNING:
            caption = "Quit"
            message = "One or more simulations are running. Do you really want to quit?"
            buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            answer = QtWidgets.QMessageBox.question(None, caption, message, buttons)

            if answer == QtWidgets.QMessageBox.No:
                event.ignore()
                return

        self.settings().write()

        await self._runner.cancel()
        await self._runner.shutdown()

        event.accept()

    def project(self):
        return self._runner.project

    async def setProject(self, project):
        if self._runner.project is not None:
            self._runner.project.simulation_added.disconnect(self.addSimulation)
            self._runner.project.simulation_recalculated.disconnect(
                self._on_simulation_recalculated
            )

        await self._runner.set_project(project)

        project.simulation_added.connect(self.addSimulation)
        project.simulation_recalculated.connect(self._on_simulation_recalculated)

        if project.filepath:
            self.settings().opendir = os.path.dirname(project.filepath)

        self.mdiarea.clear()
        self.tree.clear()

        field_project = ProjectField(self.settings(), project)
        self.tree.addField(field_project)

        for index, simulation in enumerate(project.simulations, 1):
            self.addSimulation(simulation, index)

        self.tree.expandField(field_project)

        self.setShouldSave(False)

    @asyncSlot()
    async def newProject(self):
        logger.debug("new project")
        if not self._check_save():
            return False

        await self.setProject(Project())

        self.dock_project.raise_()
        return True

    def openProject(self, filepath=None):
        if not self._check_save():
            return False

        if filepath is None:
            caption = "Open project"
            dirpath = self.settings().opendir
            namefilters = "Simulation project (*.mcsim)"
            filepath, namefilter = QtWidgets.QFileDialog.getOpenFileName(
                self, caption, dirpath, namefilters
            )

            if not namefilter:
                return False

            if not filepath:
                return False

        self.settings().opendir = os.path.dirname(filepath)

        function = functools.partial(Project.read, filepath)
        dialog = ExecutionProgressDialog(
            "Open project", "Opening project...", "Opening project...", function
        )
        dialog.exec_()

        if dialog.result() != QtWidgets.QDialog.Accepted:
            return False

        project = dialog.functionResult()
        if project is None:
            return False

        asyncio.ensure_future(self.setProject(project))

        self.dock_project.raise_()
        return True

    def saveProject(self, filepath=None):
        if filepath is None:
            filepath = self._runner.project.filepath

        if filepath is None:
            caption = "Save project"
            dirpath = self.settings().savedir
            namefilters = "Simulation project (*.mcsim)"
            filepath, namefilter = QtWidgets.QFileDialog.getSaveFileName(
                self, caption, dirpath, namefilters
            )

            if not namefilter:
                return False

            if not filepath:
                return False

        if not filepath.endswith(".mcsim"):
            filepath += ".mcsim"

        function = functools.partial(self._runner.project.write, filepath)
        dialog = ExecutionProgressDialog(
            "Save project", "Saving project...", "Project saved", function
        )
        dialog.exec_()

        self._runner.project.filepath = filepath
        self.settings().savedir = os.path.dirname(filepath)

        for field in self.tree.topLevelFields():
            self.tree.resetField(field)

        self.setShouldSave(False)

        return True

    def _add_results_to_tree(self, field_simulation, simulation):
        if simulation.results:
            for result in simulation.find_result(PhotonIntensityResultBase):
                field_result = PhotonIntensityResultField(result, self.settings())
                self.tree.addField(field_result, field_simulation)

            for result in simulation.find_result(KRatioResult):
                field_result = KRatioResultField(result, self.settings())
                self.tree.addField(field_result, field_simulation)

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
        project = field_project.project()

        # Summary table
        field_summary_table = _find_field(field_project, ProjectSummaryTableField)
        if not field_summary_table:
            field_summary_table = ProjectSummaryTableField(self.settings(), project)
            self.tree.addField(field_summary_table, field_project)

        field_summary_table.setProject(project)

        # Summary figure
        field_summary_figure = _find_field(field_project, ProjectSummaryFigureField)
        if not field_summary_figure:
            field_summary_figure = ProjectSummaryFigureField(self.settings(), project)
            self.tree.addField(field_summary_figure, field_project)

        field_summary_figure.setProject(project)

        # Simulation
        if index is None:
            index = field_project.project().simulations.index(simulation) + 1
        field_simulation = SimulationField(index, simulation)
        self.tree.addField(field_simulation, field_project)

        field_options = OptionsField(simulation.options, self.settings())
        self.tree.addField(field_options, field_simulation)
        self._add_results_to_tree(field_simulation, simulation)

        self.tree.reset()
        self.tree.expand()

        self.setShouldSave(True)

    def _on_simulation_recalculated(self, simulation):
        # Find field
        toplevelfields = self.tree.topLevelFields()
        assert len(toplevelfields) == 1
        field_project = toplevelfields[0]

        field_simulation = None
        for field in self.tree.childrenField(field_project):
            if isinstance(field, SimulationField) and field.simulation() == simulation:
                field_simulation = field
                break

        if field_simulation is None:
            return

        # Remove result fields
        for field in self.tree.childrenField(field_simulation):
            if isinstance(field, ResultFieldBase):
                self.tree.removeField(field)

        # Re-create result fields
        self._add_results_to_tree(field_simulation, simulation)

        self.tree.reset()
        self.tree.expand()

        self.setShouldSave(True)

    def settings(self):
        return self._settings

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
