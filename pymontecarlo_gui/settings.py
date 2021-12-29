""""""

# Standard library modules.
import logging

logger = logging.getLogger(__name__)

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
import pymontecarlo
from pymontecarlo.settings import Settings, XrayNotation

import pymontecarlo_gui.widgets.messagebox as messagebox
from pymontecarlo_gui.widgets.field import FieldBase

# Globals and constants variables.


class SettingsBasedField(FieldBase):

    settingsChanged = QtCore.Signal()

    def __init__(self, settings):
        self._settings = settings
        super().__init__()

    def settings(self):
        return self._settings


class PreferredUnitsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.cb_length = QtWidgets.QComboBox()
        self.cb_length.addItem("m", self._get_units_string("m"))
        self.cb_length.addItem("cm", self._get_units_string("cm"))
        self.cb_length.addItem("\u03bcm", self._get_units_string("um"))
        self.cb_length.addItem("nm", self._get_units_string("nm"))
        self.cb_length.addItem("\u212b", self._get_units_string("angstrom"))

        self.cb_density = QtWidgets.QComboBox()
        self.cb_density.addItem("g/cm\u00b3", self._get_units_string("g/cm^3"))
        self.cb_density.addItem("kg/m\u00b3", self._get_units_string("kg/m^3"))

        self.cb_energy = QtWidgets.QComboBox()
        self.cb_energy.addItem("eV", self._get_units_string("eV"))
        self.cb_energy.addItem("keV", self._get_units_string("keV"))
        #        self.cb_energy.addItem('J', self._get_units_string('J'))

        self.cb_angle = QtWidgets.QComboBox()
        self.cb_angle.addItem("\u00b0", self._get_units_string("deg"))
        self.cb_angle.addItem("rad", self._get_units_string("rad"))

        # Layouts
        layout = QtWidgets.QFormLayout()

        layout.addRow("Length/distance", self.cb_length)
        layout.addRow("Density", self.cb_density)
        layout.addRow("Energy", self.cb_energy)
        layout.addRow("Angle", self.cb_angle)

        self.setLayout(layout)

    def _get_base_units(self, unit):
        return pymontecarlo.unit_registry._get_base_units(unit)[1]

    def _get_units_string(self, unit):
        if isinstance(unit, str):
            unit = pymontecarlo.unit_registry.parse_units(unit)
        return str(unit)

    def units(self):
        return [
            self.cb_length.currentData(QtCore.Qt.UserRole),
            self.cb_density.currentData(QtCore.Qt.UserRole),
            self.cb_energy.currentData(QtCore.Qt.UserRole),
            self.cb_angle.currentData(QtCore.Qt.UserRole),
        ]

    def setUnits(self, units):
        for unit in units:
            base_units = self._get_base_units(unit)

            widget = None
            if base_units == self._get_base_units("m"):
                widget = self.cb_length
            elif base_units == self._get_base_units("g/cm^3"):
                widget = self.cb_density
            elif base_units == self._get_base_units("eV"):
                widget = self.cb_energy
            elif base_units == self._get_base_units("deg"):
                widget = self.cb_angle

            if widget:
                index = widget.findData(
                    self._get_units_string(unit), QtCore.Qt.UserRole
                )
                if index >= 0:
                    widget.setCurrentIndex(index)


class PreferredXrayWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.cb_notation = QtWidgets.QComboBox()
        self.cb_notation.addItem("IUPAC", XrayNotation.IUPAC)
        self.cb_notation.addItem("Siegbahn", XrayNotation.SIEGBAHN)

        # Layout
        layout = QtWidgets.QFormLayout()
        layout.addRow("Notation", self.cb_notation)

        self.setLayout(layout)

    def notation(self):
        return self.cb_notation.currentData(QtCore.Qt.UserRole)

    def setNotation(self, notation):
        index = self.cb_notation.findData(notation, QtCore.Qt.UserRole)
        self.cb_notation.setCurrentIndex(index)


class SettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_preferred_units = PreferredUnitsWidget()

        self.wdg_preferred_xray = PreferredXrayWidget()

        self.wdg_tab = QtWidgets.QTabWidget()
        self.wdg_tab.addTab(self.wdg_preferred_units, "Units")
        self.wdg_tab.addTab(self.wdg_preferred_xray, "X-ray")

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.wdg_tab)
        self.setLayout(layout)

    def updateSettings(self, settings):
        settings.clear_preferred_units()
        for unit in self.wdg_preferred_units.units():
            settings.set_preferred_unit(unit)

        settings.preferred_xray_notation = self.wdg_preferred_xray.notation()

    def settings(self):
        settings = Settings()
        self.updateSettings(settings)
        return settings

    def setSettings(self, settings):
        self.wdg_preferred_units.setUnits(settings.preferred_units.values())

        self.wdg_preferred_xray.setNotation(settings.preferred_xray_notation)


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Settings")

        # Widgets
        self.widget = SettingsWidget()

        buttons = QtWidgets.QDialogButtonBox()
        buttons.setStandardButtons(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Abort
        )

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.widget)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # Signals
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)

    def _on_save(self):
        settings = self.settings()

        try:
            settings.write()
        except Exception as ex:
            messagebox.exception(self, ex)
            return

        self.accept()

    def updateSettings(self, settings):
        self.widget.updateSettings(settings)

    def settings(self):
        return self.widget.settings()

    def setSettings(self, settings):
        self.widget.setSettings(settings)


def run():
    import sys

    app = QtWidgets.QApplication(sys.argv)

    dialog = SettingsDialog()
    dialog.show()

    app.exec_()


if __name__ == "__main__":
    run()
