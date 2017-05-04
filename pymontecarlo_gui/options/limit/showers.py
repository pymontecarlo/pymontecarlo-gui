""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.limit.showers import ShowersLimitBuilder

from pymontecarlo_gui.widgets.field import MultiValueField
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.options.limit.base import LimitField

# Globals and constants variables.

class NumberTrajectoriesField(MultiValueField):

    def __init__(self):
        super().__init__()

        # widgets
        self._widget = ColoredMultiFloatLineEdit()
        self._widget.setRange(1, float('inf'), 0)
        self._widget.setValues([10000])

        # Signals
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return 'Number of trajectories'

    def widget(self):
        return self._widget

    def numbersTrajectories(self):
        return self._widget.values()

    def setNumbersTrajectories(self, numbers_trajectories):
        self._widget.setValues(numbers_trajectories)

class ShowersField(LimitField):

    def __init__(self):
        super().__init__()

        self.field_number_trajectories = NumberTrajectoriesField()
        self.addLabelField(self.field_number_trajectories)

    def title(self):
        return 'Showers'

    def description(self):
        return 'Limits simulation to a number of incident trajectories'

    def limits(self):
        builder = ShowersLimitBuilder()

        for number_trajectories in self.field_number_trajectories.numbersTrajectories():
            builder.add_number_trajectories(number_trajectories)

        return super().limits() + builder.build()
