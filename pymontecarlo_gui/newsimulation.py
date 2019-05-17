""""""

# Standard library modules.
import tempfile

# Third party modules.
from qtpy import QtCore, QtWidgets
from unsync import unsync

# Local modules.
from pymontecarlo.util.error import ErrorAccumulator

from pymontecarlo_gui.widgets.icon import load_pixmap
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.widgets.field import FieldChooser, FieldToolBox
from pymontecarlo_gui.figures.sample import SampleFigureWidget
from pymontecarlo_gui.options.material import MaterialsWidget
from pymontecarlo_gui.options.options import OptionsModel
from pymontecarlo_gui.options.sample.substrate import SubstrateSampleField
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleField
from pymontecarlo_gui.options.sample.horizontallayers import HorizontalLayerSampleField
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleField
from pymontecarlo_gui.options.beam.pencil import PencilBeamField
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
        self.model.samplesChanged.connect(self._on_changed)
        self.model.beamsChanged.connect(self._on_changed)
        self.model.analysesChanged.connect(self._on_changed)

    def _on_changed(self):
        self.wdg_figure.clear()

        if not self.model.builder.samples:
            return

        self.wdg_figure.sample_figure.sample = self.model.builder.samples[0]
        self.wdg_figure.sample_figure.beams.extend(self.model.builder.beams)

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

    def isComplete(self):
        return self.field_programs.isValid()

    def registerProgramField(self, field):
        self.field_programs.addProgramField(field)

        self.field_toolbox.addField(field, False)

        field.fieldChanged.connect(self._on_program_changed)

    def programs(self):
        return self.field_programs.programs()

class ValidationThread(QtCore.QThread):

    update = QtCore.Signal(int, int)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.erraccs = {}

    @unsync
    async def runasync(self):
        options_count = self.model.optionsCount()
        self.update.emit(0, options_count)

        self.erraccs.clear()
        for i, options in enumerate(self.model.iterOptions(), 1):
            erracc = self.erraccs.setdefault(options.program.name, ErrorAccumulator())

            with tempfile.TemporaryDirectory() as dirpath:
                exporter = options.program.exporter
                await exporter._export(options, dirpath, erracc, dry_run=True)

            self.update.emit(i, options_count)

    def run(self):
        self.runasync().result()

class ValidationWizardPage(NewSimulationWizardPage):

    validateUpdate = QtCore.Signal(int, int)

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        self.setTitle('Check simulation(s)')

        # Variables
        self._thread = ValidationThread(model)

        # Widgets
        self._widget_errors = QtWidgets.QLabel()
        self._widget_errors.setWordWrap(True)

        self._progressbar = QtWidgets.QProgressBar()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._widget_errors)
        layout.addStretch()
        layout.addWidget(self._progressbar)
        self.setLayout(layout)

        # Signals
        self._thread.update.connect(self._on_thread_update)
        self._thread.finished.connect(self._on_thread_finished)

    def _errors_to_html(self, erraccs):
        html = ''

        for program_name, erracc in erraccs.items():
            html += '<h2>{}</h2>'.format(program_name)

            html += '<ul>'

            exceptions = set(str(exception) for exception in erracc.exceptions)
            if exceptions:
                for exception in sorted(exceptions):
                    html += '<li>{}</li>'.format(exception)
            else:
                html += '<li>No error</li>'

            html += '</ul>'

        return html

    def _on_thread_update(self, index, total):
        if total != self._progressbar.maximum():
            self._progressbar.setRange(0, total)

        self._progressbar.setValue(index)

        self.completeChanged.emit()

    def _on_thread_finished(self):
        self._widget_errors.setText(self._errors_to_html(self._thread.erraccs))
        self.completeChanged.emit()

    def _on_page_loaded(self):
        self._widget_errors.setText('')
        self._progressbar.setValue(0)
        self._thread.start()

    def initializePage(self):
        super().initializePage()
        QtCore.QTimer.singleShot(10, self._on_page_loaded)

    def cleanupPage(self):
        super().cleanupPage()
        self._thread.terminate()
        self._thread.wait()

    def isComplete(self):
        if self._thread.isRunning():
            return False
        if not self._thread.isFinished():
            return False

        for erracc in self._thread.erraccs.values():
            if erracc.exceptions:
                return False

        return True

#endregion

#region Wizard

class NewSimulationWizard(QtWidgets.QWizard):

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New simulation(s)')
        self.setWindowIcon(load_pixmap('logo_32x32.png'))
        self.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
        self.setMinimumSize(1000, 700)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                           QtWidgets.QSizePolicy.MinimumExpanding)

        # Variables
        self.model = OptionsModel(settings)

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

        # Validation
        self.page_validation = ValidationWizardPage(self.model)
        self.addPage(self.page_validation)

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

        page.registerBeamField(PencilBeamField())
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
        count = self.model.optionsCount()
        self.btn_count.setCount(count, estimate=True)

    def optionsList(self):
        return self.model.optionsList()

#endregion