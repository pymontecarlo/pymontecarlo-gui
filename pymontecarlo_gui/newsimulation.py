""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
import pymontecarlo
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.mock import ProgramMock, SampleMock
from pymontecarlo.options.beam import GaussianBeam

from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.figures.sample import SampleFigureWidget
from pymontecarlo_gui.options.material import MaterialsWidget
from pymontecarlo_gui.options.sample.substrate import SubstrateSampleWidget
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleWidget
from pymontecarlo_gui.options.sample.horizontallayers import HorizontalLayerSampleWidget
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleWidget
from pymontecarlo_gui.options.analysis.base import AnalysisToolBox, AnalysesWidget
from pymontecarlo_gui.options.analysis.photonintensity import PhotonIntensityAnalysisWidget
from pymontecarlo_gui.options.analysis.kratio import KRatioAnalysisWidget
from pymontecarlo_gui.options.program import ProgramsWidget, ProgramLimitsToolBox

# Globals and constants variables.

#--- Widgets

class WizardWidgetMixin:

    def wizard(self):
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'wizard'):
                return parent.wizard()
            parent = parent.parent()
        return None

#--- Widgets

class SimulationCountMockButton(QtWidgets.QAbstractButton):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._count = 0

        # Widgets
        self.label = QtWidgets.QLabel('No simulation defined')
        self.label.setAlignment(QtCore.Qt.AlignCenter)

#        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def paintEvent(self, event):
        pass

    def setCount(self, count, estimate=False):
        if count == 0:
            text = 'No simulation defined'
        elif count == 1:
            text = '{:d} simulation defined'.format(count)
        else:
            text = '{:d} simulations defined'.format(count)

        if estimate and count > 0:
            text += ' (estimation)'

        self._count = count
        self.label.setText(text)

    def count(self):
        return self._count

class PreviewWidget(QtWidgets.QWidget, WizardWidgetMixin):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_figure = SampleFigureWidget()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.wdg_figure)
        self.setLayout(layout)

    def update(self):
        self.wdg_figure.clear()

        wizard = self.wizard()
        if not wizard:
            return

        list_options, _estimated = wizard._get_options_list(estimate=True)
        if not list_options:
            return

        self.wdg_figure.sample_figure.sample = list_options[0].sample

        for options in list_options:
            self.wdg_figure.sample_figure.beams.append(options.beam)

        self.wdg_figure.draw()

#--- Pages

class NewSimulationWizardPage(QtWidgets.QWizardPage, metaclass=QABCMeta):

    def __init__(self, parent=None):
        super().__init__(parent)

class SampleWizardPage(NewSimulationWizardPage):

    samplesChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Define sample(s)")

        # Widgets
        self.wdg_materials = MaterialsWidget()

        self.cb_sample = QtWidgets.QComboBox()

        self.lbl_sample_description = QtWidgets.QLabel()
        font = self.lbl_sample_description.font()
        font.setItalic(True)
        self.lbl_sample_description.setFont(font)

        self.wdg_sample = QtWidgets.QStackedWidget()

        self.wdg_preview = PreviewWidget()

        # Layouts
        lyt_middle = QtWidgets.QVBoxLayout()
        lyt_middle.addWidget(self.cb_sample)
        lyt_middle.addWidget(self.lbl_sample_description)
        lyt_middle.addWidget(self.wdg_sample)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Materials', self.wdg_materials), 1)
        layout.addWidget(create_group_box('Definition', lyt_middle), 1)
        layout.addWidget(create_group_box('Preview', self.wdg_preview), 1)
        self.setLayout(layout)

        # Signals
        self.cb_sample.currentIndexChanged.connect(self._on_selected_sample_changed)
        self.wdg_materials.materialsChanged.connect(self._on_materials_changed)

    def _on_selected_sample_changed(self, index):
        widget_index = self.cb_sample.itemData(index)
        self.wdg_sample.setCurrentIndex(widget_index)

        widget = self.wdg_sample.widget(widget_index)
        widget.setAvailableMaterials(self.wdg_materials.materials())
        self.lbl_sample_description.setText(widget.accessibleDescription())

        self.samplesChanged.emit()
        self.wdg_preview.update()
        self.completeChanged.emit()

    def _on_materials_changed(self):
        materials = self.wdg_materials.materials()

        widget = self.wdg_sample.currentWidget()
        if widget:
            widget.setAvailableMaterials(materials)

        self.samplesChanged.emit()
        self.wdg_preview.update()
        self.completeChanged.emit()

    def _on_samples_changed(self):
        self.samplesChanged.emit()
        self.wdg_preview.update()
        self.completeChanged.emit()

    def initializePage(self):
        super().initializePage()
        self.wdg_preview.update()

    def isComplete(self):
        widget = self.wdg_sample.currentWidget()
        if not widget:
            return False
        return widget.isValid()

    def registerSampleWidget(self, widget):
        widget_index = self.wdg_sample.addWidget(widget)
        self.cb_sample.addItem(widget.accessibleName(), widget_index)

        widget.changed.connect(self._on_samples_changed)

        if self.cb_sample.count() == 1:
            self.cb_sample.setCurrentIndex(0)

    def samples(self):
        widget = self.wdg_sample.currentWidget()
        if not widget:
            return []
        return widget.samples()

class AnalysisWizardPage(NewSimulationWizardPage):

    analysesChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Select type(s) of analysis')

        # Widgets
        self.toolbox = AnalysisToolBox()

        self.wdg_analyses = AnalysesWidget()
        self.wdg_analyses.setAnalysisToolBox(self.toolbox)

        self.wdg_preview = PreviewWidget()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Analyses', self.wdg_analyses), 1)
        layout.addWidget(create_group_box('Definition', self.toolbox), 1)
        layout.addWidget(create_group_box('Preview', self.wdg_preview), 1)
        self.setLayout(layout)

        # Signals
        self.toolbox.changed.connect(self._on_analyses_changed)
        self.wdg_analyses.changed.connect(self._on_analyses_changed)

    def _on_analyses_changed(self):
        self.analysesChanged.emit()
        self.wdg_preview.update()
        self.completeChanged.emit()

    def initializePage(self):
        super().initializePage()
        self.wdg_preview.update()

    def isComplete(self):
        return self.wdg_analyses.isValid() and self.toolbox.isValid()

    def registerAnalysisWidget(self, widget):
        self.wdg_analyses.addAnalysisWidget(widget)

    def analyses(self):
        return self.wdg_analyses.selectedAnalyses()

class ProgramWizardPage(NewSimulationWizardPage):

    programsChanged = QtCore.Signal()
    limitsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Select program(s)')

        # Widgets
        self.wdg_programs = ProgramsWidget()

        self.wdg_limits = ProgramLimitsToolBox()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Programs', self.wdg_programs), 1)
        layout.addWidget(create_group_box('Limits', self.wdg_limits), 1)
        layout.addWidget(QtWidgets.QWidget(), 1)
        self.setLayout(layout)

        # Signals
        self.wdg_programs.changed.connect(self._on_programs_changed)
        self.wdg_limits.changed.connect(self._on_limits_changed)

    def _on_programs_changed(self):
        programs = self.wdg_programs.selectedPrograms()
        self.wdg_limits.setPrograms(programs)
        self.programsChanged.emit()
        self.completeChanged.emit()

    def _on_limits_changed(self):
        self.limitsChanged.emit()
        self._update_errors()
        self.completeChanged.emit()

    def _update_errors(self):
        list_options, _estimated = self.wizard()._get_options_list(estimate=True)
        programs = self.wdg_programs.programs()

        for program in programs:
            validator = program.create_validator()
            errors = set()

            for options in list_options:
                options.program = program
                validator._validate_options(options, errors)

            self.wdg_programs.setProgramErrors(program, errors)

    def initializePage(self):
        super().initializePage()
        self._update_errors()

    def isComplete(self):
        return self.wdg_programs.isValid() and self.wdg_limits.isValid()

    def registerProgram(self, program):
        self.wdg_programs.addProgram(program)

    def programs(self):
        return self.wdg_programs.selectedPrograms()

    def limits(self):
        return self.wdg_limits.limits()

#--- Wizard

class NewSimulationWizard(QtWidgets.QWizard):

    optionsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New simulation(s)')
        self.setWizardStyle(QtWidgets.QWizard.ClassicStyle)

        # Variables
        self.builder = OptionsBuilder()

        # Buttons
        self.setOption(QtWidgets.QWizard.HaveCustomButton1)
        self.setButtonLayout([QtWidgets.QWizard.CustomButton1,
                              QtWidgets.QWizard.Stretch,
                              QtWidgets.QWizard.BackButton,
                              QtWidgets.QWizard.NextButton,
                              QtWidgets.QWizard.FinishButton,
                              QtWidgets.QWizard.CancelButton])

        self.btn_count = SimulationCountMockButton()
        self.setButton(QtWidgets.QWizard.CustomButton1, self.btn_count)

        # Sample
        self.page_sample = SampleWizardPage()

        self.page_sample.registerSampleWidget(SubstrateSampleWidget())
        self.page_sample.registerSampleWidget(InclusionSampleWidget())
        self.page_sample.registerSampleWidget(HorizontalLayerSampleWidget())
        self.page_sample.registerSampleWidget(VerticalLayerSampleWidget())

        self.page_sample.samplesChanged.connect(self._on_samples_changed)

        self.addPage(self.page_sample)

        # Analysis
        self.page_analysis = AnalysisWizardPage()

        self.page_analysis.registerAnalysisWidget(PhotonIntensityAnalysisWidget())
        self.page_analysis.registerAnalysisWidget(KRatioAnalysisWidget())

        self.page_analysis.analysesChanged.connect(self._on_analyses_changed)

        self.addPage(self.page_analysis)

        # Programs
        self.page_program = ProgramWizardPage()

        for _class, program in pymontecarlo.settings.iter_programs():
            if program is None:
                continue
            self.page_program.registerProgram(program)

        self.page_program.programsChanged.connect(self._on_programs_changed)
        self.page_program.limitsChanged.connect(self._on_limits_changed)

        self.addPage(self.page_program)

        # Signals
        self.currentIdChanged.connect(self._on_options_changed)
        self.optionsChanged.connect(self._on_options_changed)

    def _on_samples_changed(self):
        self.builder.samples = self.page_sample.samples()
        self.optionsChanged.emit()

    def _on_analyses_changed(self):
        self.builder.analyses = self.page_analysis.analyses()
        self.optionsChanged.emit()

    def _on_programs_changed(self):
        self.builder.programs = self.page_program.programs()
        self.optionsChanged.emit()

    def _on_limits_changed(self):
        self.builder.limits = self.page_program.limits()
        self.optionsChanged.emit()

    def _on_options_changed(self):
        list_options, estimated = self._get_options_list(estimate=True)
        count = len(list_options)
        self.btn_count.setCount(count, estimated)

    def _get_options_list(self, estimate):
        program_mock_added = False
        if estimate and not self.builder.programs:
            self.builder.add_program(ProgramMock())
            program_mock_added = True

        beam_mock_added = False
        if estimate and not self.builder.beams:
#            self.builder.add_beam(Beam(0.0)) #TODO: Change back
            self.builder.add_beam(GaussianBeam(15e3, 10e-9))
            beam_mock_added = True

        sample_mock_added = False
        if estimate and not self.builder.samples:
            self.builder.add_sample(SampleMock())
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

        estimated = program_mock_added or beam_mock_added or sample_mock_added

        return list_options, estimated

    def optionsList(self):
        list_options, _estimated = self._get_options_list(estimate=False)
        return list_options

def run(): #pragma: no cover
    import sys

    app = QtWidgets.QApplication(sys.argv)

    wizard = NewSimulationWizard()

    wizard.exec_()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
