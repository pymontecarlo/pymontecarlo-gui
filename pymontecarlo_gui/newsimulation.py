""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
from pymontecarlo_gui.options.material import MaterialsWidget
from pymontecarlo_gui.options.sample.substrate import SubstrateSampleWidget
from pymontecarlo_gui.options.sample.inclusion import InclusionSampleWidget
from pymontecarlo_gui.options.sample.horizontallayers import HorizontalLayerSampleWidget
from pymontecarlo_gui.options.sample.verticallayers import VerticalLayerSampleWidget
from pymontecarlo_gui.figures.sample import SampleFigureWidget
from pymontecarlo_gui.widgets.groupbox import create_group_box

# Globals and constants variables.

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

    def setCount(self, count):
        if count == 0:
            text = 'No simulation defined'
        elif count > 1:
            text = '{:d} simulations defined'.format(count)
        else:
            text = '{:d} simulation defined'.format(count)

        self._count = count
        self.label.setText(text)

    def count(self):
        return self._count

class SampleWizardPage(QtWidgets.QWizardPage):

    samplesChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Define sample(s)")

        # Widgets
        self.wdg_materials = MaterialsWidget()

        self.cb_sample = QtWidgets.QComboBox()

        self.txt_sample_description = QtWidgets.QLabel()
        font = self.txt_sample_description.font()
        font.setItalic(True)
        self.txt_sample_description.setFont(font)

        self.wdg_sample = QtWidgets.QStackedWidget()

        self.wdg_figure = SampleFigureWidget()

        # Layouts
        lyt_middle = QtWidgets.QVBoxLayout()
        lyt_middle.addWidget(self.cb_sample)
        lyt_middle.addWidget(self.txt_sample_description)
        lyt_middle.addWidget(self.wdg_sample)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(create_group_box('Materials', self.wdg_materials), 1)
        layout.addWidget(create_group_box('Definition', lyt_middle), 1)
        layout.addWidget(create_group_box('Preview', self.wdg_figure), 1)
        self.setLayout(layout)

        # Signals
        self.cb_sample.currentIndexChanged.connect(self._on_selected_sample_changed)

        self.wdg_materials.materialsChanged.connect(self._on_materials_changed)

        self.samplesChanged.connect(self.completeChanged)

    def _on_selected_sample_changed(self, index):
        widget_index = self.cb_sample.itemData(index)
        self.wdg_sample.setCurrentIndex(widget_index)

        widget = self.wdg_sample.widget(widget_index)
        widget.setAvailableMaterials(self.wdg_materials.materials())
        self.txt_sample_description.setText(widget.accessibleDescription())

        self._update_figure()
        self.samplesChanged.emit()

    def _on_materials_changed(self):
        materials = self.wdg_materials.materials()
        self.wdg_sample.currentWidget().setAvailableMaterials(materials)

        self._update_figure()
        self.samplesChanged.emit()

    def _on_samples_changed(self):
        self._update_figure()
        self.samplesChanged.emit()

    def _update_figure(self):
        widget = self.wdg_sample.currentWidget()
        samples = widget.samples()
        if samples:
            self.wdg_figure.setSample(samples[0])
        else:
            self.wdg_figure.setSample(None)

    def isComplete(self):
        return self.wdg_sample.currentWidget().isValid()

    def registerSampleWidget(self, widget):
        widget_index = self.wdg_sample.addWidget(widget)
        self.cb_sample.addItem(widget.accessibleName(), widget_index)

        widget.changed.connect(self._on_samples_changed)

        if self.cb_sample.count() == 1:
            self.cb_sample.setCurrentIndex(0)

    def samples(self):
        return self.wdg_sample.currentWidget().samples()

class NewSimulationWizard(QtWidgets.QWizard):

    optionsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New simulation(s)')
        self.setOption(QtWidgets.QWizard.IndependentPages)
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
        self.sample_page = SampleWizardPage()

        self.sample_page.registerSampleWidget(SubstrateSampleWidget())
        self.sample_page.registerSampleWidget(InclusionSampleWidget())
        self.sample_page.registerSampleWidget(HorizontalLayerSampleWidget())
        self.sample_page.registerSampleWidget(VerticalLayerSampleWidget())

        self.sample_page.samplesChanged.connect(self.optionsChanged)

        self.addPage(self.sample_page)

        # Signals
        self.optionsChanged.connect(self._on_options_changed)

    def _on_options_changed(self):
        self.btn_count.setCount(len(self.samples()))

    def options(self):
        raise NotImplementedError

    def optionsCount(self):
        raise NotImplementedError

    def samples(self):
        return self.sample_page.samples()

def run(): #pragma: no cover
    import sys

    app = QtWidgets.QApplication(sys.argv)

    wizard = NewSimulationWizard()

    wizard.exec_()

    app.exec_()

if __name__ == '__main__': #pragma: no cover
    run()
