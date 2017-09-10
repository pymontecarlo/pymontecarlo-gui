""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.mock import ProgramMock, ProgramBuilderMock
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel

from pymontecarlo_gui.options.program.base import ProgramField
from pymontecarlo_gui.options.model.elastic_cross_section import ElasticCrossSectionModelField
from pymontecarlo_gui.widgets.field import MultiValueField
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit

# Globals and constants variables.

class FooField(MultiValueField):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = ColoredMultiFloatLineEdit()
        self._widget.setRange(0, 1000, 0)
        self._widget.setValues([123])

        # Signals
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Foo'

    def widget(self):
        return self._widget

    def foos(self):
        return self._widget.values()

    def setFoos(self, foos):
        self._widget.setValues(foos)

class ProgramFieldMock(ProgramField):

    def __init__(self):
        default_program = ProgramMock()
        super().__init__(default_program)

        self.field_foo = FooField()
        self.addLabelField(self.field_foo)

        self.field_elastic_cross_section_model = ElasticCrossSectionModelField()
        for model in self._validator.valid_models[ElasticCrossSectionModel]:
            checked = model == default_program.elastic_cross_section_model
            self.field_elastic_cross_section_model.addModel(model, checked)
        self.addGroupField(self.field_elastic_cross_section_model)

    def title(self):
        return 'Mock'

    def programs(self):
        builder = ProgramBuilderMock()

        for foo in self.field_foo.foos():
            builder.add_foo(foo)

        for model in self.field_elastic_cross_section_model.selectedModels():
            builder.add_elastic_cross_section_model(model)

        return super().programs() + builder.build()
