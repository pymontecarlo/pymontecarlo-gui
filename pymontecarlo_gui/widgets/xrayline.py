""""""

# Standard library modules.

# Third party modules.
from qtpy import QtWidgets

# Local modules.
from pymontecarlo_gui.widgets.field import FieldBase

from pymontecarlo.settings import XrayNotation

# Globals and constants variables.


class XrayLineField(FieldBase):
    def __init__(self, settings):
        super().__init__()

        # Variables
        self.settings = settings

        # Widgets
        self._widget = QtWidgets.QComboBox()

        # Signals
        settings.settings_changed.connect(self._on_settings_changed)

        self._widget.currentIndexChanged.connect(self.fieldChanged)

    def _on_settings_changed(self):
        for index in range(self._widget.count()):
            xrayline = self._widget.itemData(index)
            text = self._get_xrayline_text(xrayline)
            self._widget.setItemText(index, text)

    def _get_xrayline_text(self, xrayline):
        if self.settings.preferred_xray_notation == XrayNotation.SIEGBAHN:
            notation = xrayline.siegbahn
        else:
            notation = xrayline.iupac

        return "{} ({:.0f}eV)".format(notation, xrayline.energy_eV)

    def title(self):
        return "X-ray line"

    def widget(self):
        return self._widget

    def isValid(self):
        return super().isValid() and self._widget.currentIndex() >= 0

    def setXrayLines(self, xraylines):
        self._widget.clear()

        for xrayline in xraylines:
            text = self._get_xrayline_text(xrayline)
            self._widget.addItem(text, userData=xrayline)

    def xrayLines(self):
        xraylines = []
        for index in range(self._widget.count()):
            xrayline = self._widget.itemData(index)
            xraylines.append(xrayline)

        return tuple(xraylines)

    def selectedXrayLine(self):
        return self._widget.currentData()

    def setSelectedXrayLine(self, xrayline):
        index = self._widget.findData(xrayline)
        self._widget.setCurrentIndex(index)
