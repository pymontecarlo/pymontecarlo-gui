""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo.options.limit.showers import ShowersLimitBuilder

from pymontecarlo_gui.widgets.field import Field, FieldLayout
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.options.limit.base import LimitWidget

# Globals and constants variables.

class NumberTrajectoriesField(Field):

    def __init__(self):
        super().__init__()

        # widgets
        self._label = QtWidgets.QLabel('Number of trajectories')

        self._widget = ColoredMultiFloatLineEdit()
        self._widget.setRange(1, float('inf'), 0)
        self._widget.setValues([10000])

        # Signals
        self._widget.valuesChanged.connect(self.changed)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def numbersTrajectories(self):
        return self._widget.values()

    def setNumbersTrajectories(self, numbers_trajectories):
        self._widget.setValues(numbers_trajectories)

class ShowersWidget(LimitWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName('Showers')
        self.setAccessibleDescription('Limits simulation to a number of incident trajectories')

        # widgets
        self.field_number_trajectories = NumberTrajectoriesField()

        # Layouts
        layout = FieldLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLabelField(self.field_number_trajectories)
        self.setLayout(layout)

        # Signals
        self.field_number_trajectories.changed.connect(self.changed)

    def isValid(self):
        return super().isValid() and \
            self.field_number_trajectories.isValid()

    def limits(self):
        builder = ShowersLimitBuilder()

        for number_trajectories in self.field_number_trajectories.numbersTrajectories():
            builder.add_number_trajectories(number_trajectories)

        return super().limits() + builder.build()
