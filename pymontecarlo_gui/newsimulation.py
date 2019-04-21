""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.widgets.field import FieldChooser, FieldToolBox
from pymontecarlo_gui.figures.sample import SampleFigureWidget
from pymontecarlo_gui.options.material import MaterialsWidget
from pymontecarlo_gui.options.options import OptionsModel
from pymontecarlo_gui.options.sample.substrate import SubstrateSampleField
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleField
from pymontecarlo_gui.options.sample.horizontallayers import HorizontalLayerSampleField
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleField
from pymontecarlo_gui.options.beam.gaussian import GaussianBeamField
from pymontecarlo_gui.options.beam.cylindrical import CylindricalBeamField
from pymontecarlo_gui.options.analysis.base import AnalysesField
from pymontecarlo_gui.options.analysis.photonintensity import PhotonIntensityAnalysisField
from pymontecarlo_gui.options.analysis.kratio import KRatioAnalysisField
from pymontecarlo_gui.options.program.base import ProgramsField, ProgramFieldBase

# Globals and constants variables.

#region Widgets

class SimulationCountMockButton(QtWidgets.QAbstractButton):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._count = 0

        # Widgets
        self.label = QtWidgets.QLabel('No simulation defined')
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Layouts
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

class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, model, parent=None):
        super().__init__(parent)

        # Variables
        self.model = model

        # Widgets
        self.wdg_figure = SampleFigureWidget()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.wdg_figure)
        self.setLayout(layout)

        # Signals
        self.model.optionsChanged.connect(self._on_options_changed)

    def _on_options_changed(self):
        self.wdg_figure.clear()

        list_options = self.model.getOptionsList(estimate=True)
        if not list_options:
            return

        self.wdg_figure.sample_figure.sample = list_options[0].sample

        for options in list_options:
            self.wdg_figure.sample_figure.beams.append(options.beam)

        self.wdg_figure.draw()

#endregion

#region Pages

class NewSimulationWizardPage(QtWidgets.QWizardPage):

    def __init__(self, model, parent=None):
        super().__init__(parent)

        # Variables
        self.model = model

class SampleWizardPage(NewSimulationWizardPage):

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        self.setTitle("Define sample(s)")

        # Widgets
        self.wdg_materials = MaterialsWidget()

        self.wdg_sample = FieldChooser()

        self.widget_preview = PreviewWidget(model)

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

        self.model.setSamples(self.samples())
        self.completeChanged.emit()

    def _on_materials_changed(self):
        materials = self.wdg_materials.materials()

        field = self.wdg_sample.currentField()
        if field:
            field.setAvailableMaterials(materials)

        self.completeChanged.emit()

    def _on_samples_changed(self):
        self.model.setSamples(self.samples())
        self.completeChanged.emit()

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

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        self.setTitle("Define incident beam(s)")

        # Widgets
        self.wdg_beam = FieldChooser()

        self.widget_preview = PreviewWidget(model)

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Beams', self.wdg_beam), 1)
        layout.addWidget(create_group_box('Preview', self.widget_preview), 1)
        self.setLayout(layout)

        # Signals
        self.wdg_beam.currentFieldChanged.connect(self._on_selected_beam_changed)

    def _on_selected_beam_changed(self, field):
        self.model.setBeams(self.beams())
        self.completeChanged.emit()

    def _on_beams_changed(self):
        self.model.setBeams(self.beams())
        self.completeChanged.emit()

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

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        self.setTitle('Select type(s) of analysis')

        # Variables
        self._definition_field_classes = {}

        # Widgets
        self.field_analyses = AnalysesField()

        self.field_toolbox = FieldToolBox()

        self.widget_preview = PreviewWidget(model)

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box(self.field_analyses.title(), self.field_analyses.widget()), 1)
        layout.addWidget(create_group_box('Definition', self.field_toolbox), 1)
        layout.addWidget(create_group_box('Preview', self.widget_preview), 1)
        self.setLayout(layout)

    def _on_analyses_changed(self):
        selected_analysis_fields = self.field_analyses.selectedAnalysisFields()

        definition_fields = set()
        for field in selected_analysis_fields:
            definition_field = field.definitionField()
            definition_fields.add(definition_field)
        self.field_toolbox.setSelectedFields(definition_fields)

        self.model.setAnalyses(self.analyses())
        self.completeChanged.emit()

    def isComplete(self):
        return self.field_analyses.isValid() and self.field_toolbox.isValid()

    def registerAnalysisField(self, field):
        self.field_analyses.addAnalysisField(field)

        definition_field_class = field.definitionFieldClass()
        definition_field = self._definition_field_classes.get(definition_field_class)
        if definition_field is None:
            definition_field = field.definitionField()
            self.field_toolbox.addField(definition_field, False)
            self._definition_field_classes[definition_field_class] = definition_field
            definition_field.fieldChanged.connect(self._on_analyses_changed)
        else:
            field.setDefinitionField(definition_field)

        field.fieldChanged.connect(self._on_analyses_changed)

    def analyses(self):
        return self.field_analyses.selectedAnalyses()

class ProgramWizardPage(NewSimulationWizardPage):

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        self.setTitle('Select program(s)')

        # Widgets
        self.field_programs = ProgramsField()

        self.field_toolbox = FieldToolBox()

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box(self.field_programs.title(), self.field_programs.widget()), 1)
        layout.addWidget(create_group_box('Definition', self.field_toolbox), 1)
        self.setLayout(layout)

        # Signals
        self.field_programs.fieldChanged.connect(self._on_selected_programs_changed)

    def _on_selected_programs_changed(self):
        fields = self.field_programs.selectedProgramFields()
        self.field_toolbox.setSelectedFields(fields)

        self.model.setPrograms(self.programs())
        self.completeChanged.emit()

    def _on_program_changed(self):
        self.model.setPrograms(self.programs())
        self.completeChanged.emit()

    def _update_errors(self):
        list_options = self.model.getOptionsList(estimate=True)
        self.field_programs.updateErrors(list_options)

    def initializePage(self):
        super().initializePage()
        self._update_errors()

    def isComplete(self):
        return self.field_programs.isValid()

    def registerProgramField(self, field):
        self.field_programs.addProgramField(field)

        self.field_toolbox.addField(field, False)

        field.fieldChanged.connect(self._on_program_changed)

    def programs(self):
        return self.field_programs.programs()

#endregion

#region Wizard

class NewSimulationWizard(QtWidgets.QWizard):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New simulation(s)')
        self.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
        self.setMinimumSize(1000, 700)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                           QtWidgets.QSizePolicy.MinimumExpanding)

        # Variables
        self.model = OptionsModel()

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
        self.page_sample = self._create_sample_page()
        self.addPage(self.page_sample)

        # Beam
        self.page_beam = self._create_beam_page()
        self.addPage(self.page_beam)

        # Analysis
        self.page_analysis = self._create_analysis_page()
        self.addPage(self.page_analysis)

        # Programs
        self.page_program = self._create_program_page()
        self.addPage(self.page_program)

        # Signals
        self.currentIdChanged.connect(self._on_options_changed)
        self.model.optionsChanged.connect(self._on_options_changed)

    def _create_sample_page(self):
        page = SampleWizardPage(self.model)

        page.registerSampleField(SubstrateSampleField())
        page.registerSampleField(InclusionSampleField())
        page.registerSampleField(HorizontalLayerSampleField())
        page.registerSampleField(VerticalLayerSampleField())

        return page

    def _create_beam_page(self):
        page = BeamWizardPage(self.model)

        page.registerBeamField(GaussianBeamField())
        page.registerBeamField(CylindricalBeamField())

        return page

    def _create_analysis_page(self):
        page = AnalysisWizardPage(self.model)

        page.registerAnalysisField(PhotonIntensityAnalysisField())
        page.registerAnalysisField(KRatioAnalysisField())

        return page

    def _create_program_page(self):
        page = ProgramWizardPage(self.model)

        for clasz in ProgramFieldBase._subclasses:
            field = clasz(self.model)
            page.registerProgramField(field)

        return page

    def _on_options_changed(self):
        estimated = self.model.isOptionListEstimated()
        list_options = self.model.getOptionsList(estimated)
        count = len(list_options)
        self.btn_count.setCount(count, estimated)

    def optionsList(self):
        return self.model.getOptionsList()

#endregion