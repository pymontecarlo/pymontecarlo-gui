""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
import pymontecarlo
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.mock import ProgramMock, SampleMock
from pymontecarlo.options.beam.base import Beam
from pymontecarlo.options.limit.showers import ShowersLimit

from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.widgets.field import FieldChooser
from pymontecarlo_gui.figures.sample import SampleFigureWidget
from pymontecarlo_gui.options.material import MaterialsWidget
from pymontecarlo_gui.options.sample.substrate import SubstrateSampleField
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleField
from pymontecarlo_gui.options.sample.horizontallayers import HorizontalLayerSampleField
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleField
from pymontecarlo_gui.options.beam.gaussian import GaussianBeamField
from pymontecarlo_gui.options.beam.cylindrical import CylindricalBeamField
from pymontecarlo_gui.options.analysis.base import AnalysesField, AnalysesToolBoxField
from pymontecarlo_gui.options.analysis.photonintensity import PhotonIntensityAnalysisField
from pymontecarlo_gui.options.analysis.kratio import KRatioAnalysisField
from pymontecarlo_gui.options.limit.showers import ShowersField
from pymontecarlo_gui.options.program import ProgramsField, LimitsToolBoxField

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

        self.wdg_sample = FieldChooser()

        self.widget_preview = PreviewWidget()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Materials', self.wdg_materials), 1)
        layout.addWidget(create_group_box('Definition', self.wdg_sample), 1)
        layout.addWidget(create_group_box('Preview', self.widget_preview), 1)
        self.setLayout(layout)

        # Signals
        self.wdg_sample.currentFieldChanged.connect(self._on_selected_sample_changed)
        self.wdg_materials.materialsChanged.connect(self._on_materials_changed)

    def _on_selected_sample_changed(self, field):
        materials = self.wdg_materials.materials()
        field.setAvailableMaterials(materials)

        self.samplesChanged.emit()
        self.widget_preview.update()
        self.completeChanged.emit()

    def _on_materials_changed(self):
        materials = self.wdg_materials.materials()

        field = self.wdg_sample.currentField()
        if field:
            field.setAvailableMaterials(materials)

        self.samplesChanged.emit()
        self.widget_preview.update()
        self.completeChanged.emit()

    def _on_samples_changed(self):
        self.samplesChanged.emit()
        self.widget_preview.update()
        self.completeChanged.emit()

    def initializePage(self):
        super().initializePage()
        self.widget_preview.update()

    def isComplete(self):
        field = self.wdg_sample.currentField()
        if not field:
            return False
        return field.isValid()

    def registerSampleField(self, field):
        self.wdg_sample.addField(field)
        field.fieldChanged.connect(self._on_samples_changed)

    def samples(self):
        field = self.wdg_sample.currentField()
        if not field:
            return []
        return field.samples()

class BeamWizardPage(NewSimulationWizardPage):

    beamsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Define incident beam(s)")

        # Widgets
        self.wdg_beam = FieldChooser()

        self.widget_preview = PreviewWidget()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Beams', self.wdg_beam), 1)
        layout.addWidget(create_group_box('Preview', self.widget_preview), 1)
        self.setLayout(layout)

        # Signals
        self.wdg_beam.currentFieldChanged.connect(self._on_selected_beam_changed)

    def _on_selected_beam_changed(self, field):
        self.beamsChanged.emit()
        self.widget_preview.update()
        self.completeChanged.emit()

    def _on_beams_changed(self):
        self.beamsChanged.emit()
        self.widget_preview.update()
        self.completeChanged.emit()

    def initializePage(self):
        super().initializePage()
        self.beamsChanged.emit()
        self.widget_preview.update()

    def isComplete(self):
        field = self.wdg_beam.currentField()
        if not field:
            return False
        return field.isValid()

    def registerBeamField(self, field):
        self.wdg_beam.addField(field)
        field.fieldChanged.connect(self._on_beams_changed)

    def beams(self):
        field = self.wdg_beam.currentField()
        if not field:
            return []
        return field.beams()

class AnalysisWizardPage(NewSimulationWizardPage):

    analysesChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Select type(s) of analysis')

        # Widgets
        self.field_analyses_toolbox = AnalysesToolBoxField()

        self.field_analyses = AnalysesField()
        self.field_analyses.setAnalysesToolBoxField(self.field_analyses_toolbox)

        self.widget_preview = PreviewWidget()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Analyses', self.field_analyses.widget()), 1)
        layout.addWidget(create_group_box('Definition', self.field_analyses_toolbox.widget()), 1)
        layout.addWidget(create_group_box('Preview', self.widget_preview), 1)
        self.setLayout(layout)

        # Signals
        self.field_analyses_toolbox.fieldChanged.connect(self._on_analyses_changed)
        self.field_analyses.fieldChanged.connect(self._on_analyses_changed)

    def _on_analyses_changed(self):
        self.analysesChanged.emit()
        self.widget_preview.update()
        self.completeChanged.emit()

    def initializePage(self):
        super().initializePage()
        self.widget_preview.update()

    def isComplete(self):
        return self.field_analyses.isValid() and self.field_analyses_toolbox.isValid()

    def registerAnalysisField(self, field):
        self.field_analyses.addAnalysisField(field)

    def analyses(self):
        return self.field_analyses.selectedAnalyses()

class ProgramWizardPage(NewSimulationWizardPage):

    programsChanged = QtCore.Signal()
    limitsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Select program(s)')

        # Widgets
        self.field_programs = ProgramsField()

        self.field_limits = LimitsToolBoxField()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Programs', self.field_programs.widget()), 1)
        layout.addWidget(create_group_box('Limits', self.field_limits.widget()), 1)
        self.setLayout(layout)

        # Signals
        self.field_programs.fieldChanged.connect(self._on_programs_changed)
        self.field_limits.fieldChanged.connect(self._on_limits_changed)

    def _on_programs_changed(self):
        programs = self.field_programs.selectedPrograms()
        self.field_limits.setPrograms(programs)
        self.programsChanged.emit()
        self.completeChanged.emit()

    def _on_limits_changed(self):
        self.limitsChanged.emit()
        self._update_errors()
        self.completeChanged.emit()

    def _update_errors(self):
        list_options, _estimated = self.wizard()._get_options_list(estimate=True)
        programs = self.field_programs.programs()

        for program in programs:
            validator = program.create_validator()
            errors = set()

            for options in list_options:
                options.program = program
                validator._validate_options(options, errors)

            self.field_programs.setProgramErrors(program, errors)

    def initializePage(self):
        super().initializePage()
        self._update_errors()

    def isComplete(self):
        return self.field_programs.isValid() and self.field_limits.isValid()

    def registerLimitFieldClass(self, option_class, field_class):
        self.field_limits.registerLimitFieldClass(option_class, field_class)

    def registerProgram(self, program):
        self.field_programs.addProgram(program)

    def programs(self):
        return self.field_programs.selectedPrograms()

    def limits(self):
        return self.field_limits.limits()

#--- Wizard

class NewSimulationWizard(QtWidgets.QWizard):

    optionsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New simulation(s)')
        self.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
        self.setMinimumSize(1000, 700)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                           QtWidgets.QSizePolicy.MinimumExpanding)

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

        self.page_sample.registerSampleField(SubstrateSampleField())
        self.page_sample.registerSampleField(InclusionSampleField())
        self.page_sample.registerSampleField(HorizontalLayerSampleField())
        self.page_sample.registerSampleField(VerticalLayerSampleField())

        self.page_sample.samplesChanged.connect(self._on_samples_changed)

        self.addPage(self.page_sample)

        # Beam
        self.page_beam = BeamWizardPage()

        self.page_beam.registerBeamField(GaussianBeamField())
        self.page_beam.registerBeamField(CylindricalBeamField())

        self.page_beam.beamsChanged.connect(self._on_beams_changed)

        self.addPage(self.page_beam)

        # Analysis
        self.page_analysis = AnalysisWizardPage()

        self.page_analysis.registerAnalysisField(PhotonIntensityAnalysisField())
        self.page_analysis.registerAnalysisField(KRatioAnalysisField())

        self.page_analysis.analysesChanged.connect(self._on_analyses_changed)

        self.addPage(self.page_analysis)

        # Programs
        self.page_program = ProgramWizardPage()

        self.page_program.registerLimitFieldClass(ShowersLimit, ShowersField)

        for program in pymontecarlo.settings.activated_programs:
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

    def _on_beams_changed(self):
        self.builder.beams = self.page_beam.beams()
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
            self.builder.add_beam(Beam(0.0)) #TODO: Change back
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
