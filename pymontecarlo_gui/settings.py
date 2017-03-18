""""""

# Standard library modules.
import functools
import logging
logger = logging.getLogger(__name__)
import argparse

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
import pymontecarlo
from pymontecarlo._settings import Settings
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.program.configurator import FileType, DirectoryType

from pymontecarlo_gui.widgets.util import clear_stackedwidget, create_group_box
from pymontecarlo_gui.widgets.label import LabelIcon
import pymontecarlo_gui.widgets.messagebox as messagebox
from pymontecarlo_gui.widgets.browse import FileBrowseWidget, DirectoryBrowseWidget

# Globals and constants variables.

class ProgramWidget(QtWidgets.QWidget):

    edited = QtCore.Signal(object)

    def __init__(self, program_class, parent=None):
        super().__init__(parent)

        # Variables
        self.program_class = program_class
        self.configurator = program_class.create_configurator()

        self.widgets_functions = {}

        _parser, actions = self._create_dummy_parser()

        # Program widgets
        lyt_action = QtWidgets.QFormLayout()

        for action in actions:
            label = action.option_strings[0].replace('-', '').capitalize()

            if action.type is FileType:
                widget = FileBrowseWidget()

                widget.pathChanged.connect(self._on_edited)

                getfunc = lambda : widget.path()
                setfunc = lambda value: widget.setPath(value)

            elif action.type is DirectoryType:
                widget = DirectoryBrowseWidget()

                widget.pathChanged.connect(self._on_edited)

                getfunc = lambda : widget.path()
                setfunc = lambda value: widget.setPath(value)

            else:
                widget = QtWidgets.QLineEdit()

                widget.textChanged.connect(self._on_edited)

                getfunc = lambda : widget.text()
                setfunc = lambda value: widget.setText(value)

            self.widgets_functions[action.dest] = (getfunc, setfunc)

            widget.setToolTip(action.help)
            lyt_action.addRow(label, widget)

        # Widgets
        lbl_name = QtWidgets.QLabel(self.configurator.fullname)
        font = lbl_name.font()
        font.setBold(True)
        font.setPointSize(14)
        lbl_name.setFont(font)

        self.lbl_error = LabelIcon('', QtGui.QIcon.fromTheme("dialog-error"))
        self.lbl_error.setVisible(False)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(lbl_name)
        layout.addLayout(lyt_action)
        layout.addStretch()
        layout.addWidget(self.lbl_error)

        self.setLayout(layout)

    def _create_dummy_parser(self, program=None):
        parser = argparse.ArgumentParser()
        self.configurator.prepare_parser(parser, program)

        actions = [a for a in parser._actions if isinstance(a, argparse._StoreAction)]

        return parser, actions

    def _on_edited(self, *args):
        try:
            program = self.program()

            validator = program.create_validator()
            validator.validate_program(program, None)
        except Exception as ex:
            self.lbl_error.setText(str(ex))
            self.lbl_error.setVisible(True)
            self.edited.emit(None)
        else:
            self.lbl_error.setVisible(False)
            self.edited.emit(program)

    def setProgram(self, program):
        _parser, actions = self._create_dummy_parser(program)

        for action in actions:
            if action.dest not in self.widgets_functions:
                continue
            setfunc = self.widgets_functions[action.dest][1]
            setfunc(action.default)

        self._on_edited()

    def program(self):
        parser, actions = self._create_dummy_parser()

        args = []
        for action in actions:
            if action.dest not in self.widgets_functions:
                continue

            getfunc = self.widgets_functions[action.dest][0]
            value = getfunc()

            args += [action.option_strings[0], value]

        namespace = parser.parse_args(args)

        return self.configurator.create_program(namespace, self.program_class)

class ProgramsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables

        # Widgets
        self.cb_available_programs = QtWidgets.QComboBox()
        self.cb_available_programs.setMinimumWidth(175)

        self.lst_configured_programs = QtWidgets.QListWidget()
        self.lst_configured_programs.setIconSize(QtCore.QSize(16, 16))
        self.lst_configured_programs.setMaximumWidth(175)

        self.btn_activate = QtWidgets.QPushButton('Activate')

        self.btn_deactivate = QtWidgets.QPushButton('Deactivate')

        self.wdg_programs = QtWidgets.QStackedWidget()

        # Layouts
        lyt_top = QtWidgets.QHBoxLayout()
        lyt_top.addWidget(QtWidgets.QLabel('Available program(s)'))
        lyt_top.addWidget(self.cb_available_programs, 1)
        lyt_top.addWidget(self.btn_activate)

        lyt_right = QtWidgets.QVBoxLayout()
        lyt_right.addWidget(QtWidgets.QLabel('Configured program(s)'))
        lyt_right.addWidget(self.lst_configured_programs)
        lyt_right.addWidget(self.btn_deactivate)

        layout = QtWidgets.QGridLayout()
        layout.addLayout(lyt_top, 0, 1)
        layout.addLayout(lyt_right, 1, 0)
        layout.addWidget(self.wdg_programs, 1, 1)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 2)
        self.setLayout(layout)

        # Signals
        self.lst_configured_programs.clicked.connect(self._on_configured_programs_clicked)
        self.btn_activate.clicked.connect(self._on_activate)
        self.btn_deactivate.clicked.connect(self._on_deactivate)

    def _on_program_edited(self, item, program):
        if program is None:
            item.setIcon(QtGui.QIcon.fromTheme("dialog-error"))
        else:
            item.setIcon(QtGui.QIcon())

    def _on_configured_programs_clicked(self, index):
        item = self.lst_configured_programs.item(index.row())
        widget_index = item.data(QtCore.Qt.UserRole)
        self.wdg_programs.setCurrentIndex(widget_index)

    def _on_deactivate(self):
        index = self.lst_configured_programs.currentIndex()
        row = index.row()
        if row < 0:
            return

        # Remove from configured
        item = self.lst_configured_programs.takeItem(row)

        # Add to available
        fullname = item.text()
        widget_index = item.data(QtCore.Qt.UserRole)
        self._add_to_available(fullname, widget_index)

        # Check current widget
        if self.wdg_programs.currentIndex() == widget_index:
            self.wdg_programs.setCurrentIndex(0)

        # Update buttons
        self._update_buttons()

    def _on_activate(self):
        index = self.cb_available_programs.currentIndex()
        if index < 0:
            return

        # Remove from available
        widget_index = self.cb_available_programs.itemData(index, QtCore.Qt.UserRole)
        fullname = self.cb_available_programs.itemText(index)
        self.cb_available_programs.removeItem(index)

        # Add to configured
        item = self._add_to_configured(fullname, widget_index)

        # Update current widget
        self.lst_configured_programs.setCurrentItem(item)
        self.wdg_programs.setCurrentIndex(widget_index)

        # Update buttons
        self._update_buttons()

    def _update_buttons(self):
        has_configured = self.lst_configured_programs.count() > 0
        self.btn_deactivate.setEnabled(has_configured)

        has_available = self.cb_available_programs.count() > 0
        self.btn_activate.setEnabled(has_available)

    def _add_to_configured(self, fullname, widget_index):
        item = QtWidgets.QListWidgetItem(fullname)
        item.setData(QtCore.Qt.UserRole, widget_index)
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lst_configured_programs.addItem(item)

        wdg_program = self.wdg_programs.widget(widget_index)
        wdg_program.edited.connect(functools.partial(self._on_program_edited, item))

        wdg_program._on_edited() # To refresh status

        return item

    def _add_to_available(self, fullname, widget_index):
        self.cb_available_programs.addItem(fullname, widget_index)

    def setPrograms(self, programs):
        # Clear
        self.cb_available_programs.clear()
        self.lst_configured_programs.clear()
        clear_stackedwidget(self.wdg_programs)

        self.wdg_programs.addWidget(QtWidgets.QWidget()) # Empty widget

        # Create widget, add to appropriate list
        for clasz, program in pymontecarlo.settings.iter_programs():
            if program is not None and program not in programs:
                continue

            fullname = clasz.create_configurator().fullname

            wdg_program = ProgramWidget(clasz)
            widget_index = self.wdg_programs.addWidget(wdg_program)

            if program is None:
                self._add_to_available(fullname, widget_index)
            else:
                self._add_to_configured(fullname, widget_index)
                wdg_program.setProgram(program)

        # Update buttons
        self._update_buttons()

    def programs(self):
        programs = []

        for index in range(self.lst_configured_programs.count()):
            item = self.lst_configured_programs.item(index)
            widget_index = item.data(QtCore.Qt.UserRole)
            widget = self.wdg_programs.widget(widget_index)
            programs.append(widget.program())

        return programs

class PreferredUnitsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.cb_length = QtWidgets.QComboBox()
        self.cb_length.addItem('m', self._get_units_string('m'))
        self.cb_length.addItem('cm', self._get_units_string('cm'))
        self.cb_length.addItem('\u03bcm', self._get_units_string('um'))
        self.cb_length.addItem('nm', self._get_units_string('nm'))
        self.cb_length.addItem('\u212b', self._get_units_string('angstrom'))

        self.cb_density = QtWidgets.QComboBox()
        self.cb_density.addItem('g/cm\u00b3', self._get_units_string('g/cm^3'))
        self.cb_density.addItem('kg/m\u00b3', self._get_units_string('kg/m^3'))

        self.cb_energy = QtWidgets.QComboBox()
        self.cb_energy.addItem('eV', self._get_units_string('eV'))
        self.cb_energy.addItem('keV', self._get_units_string('keV'))
#        self.cb_energy.addItem('J', self._get_units_string('J'))

        self.cb_angle = QtWidgets.QComboBox()
        self.cb_angle.addItem('\u00b0', self._get_units_string('deg'))
        self.cb_angle.addItem('rad', self._get_units_string('rad'))

        # Layouts
        layout = QtWidgets.QFormLayout()

        layout.addRow('Length/distance', self.cb_length)
        layout.addRow('Density', self.cb_density)
        layout.addRow('Energy', self.cb_energy)
        layout.addRow('Angle', self.cb_angle)

        self.setLayout(layout)

    def _get_base_units(self, unit):
        return pymontecarlo.unit_registry._get_base_units(unit)[1]

    def _get_units_string(self, unit):
        if isinstance(unit, str):
            unit = pymontecarlo.unit_registry.parse_units(unit)
        return str(unit)

    def units(self):
        return [self.cb_length.currentData(QtCore.Qt.UserRole),
                self.cb_density.currentData(QtCore.Qt.UserRole),
                self.cb_energy.currentData(QtCore.Qt.UserRole),
                self.cb_angle.currentData(QtCore.Qt.UserRole)]

    def setUnits(self, units):
        for unit in units:
            base_units = self._get_base_units(unit)

            widget = None
            if base_units == self._get_base_units('m'):
                widget = self.cb_length
            elif base_units == self._get_base_units('g/cm^3'):
                widget = self.cb_density
            elif base_units == self._get_base_units('eV'):
                widget = self.cb_energy
            elif base_units == self._get_base_units('deg'):
                widget = self.cb_angle

            if widget:
                index = widget.findData(self._get_units_string(unit), QtCore.Qt.UserRole)
                if index >= 0:
                    widget.setCurrentIndex(index)

class PreferredXrayLineWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.cb_notation = QtWidgets.QComboBox()
        self.cb_notation.addItem('IUPAC', 'iupac')
        self.cb_notation.addItem('Siegbahn', 'siegbahn')

        # Layout
        layout = QtWidgets.QFormLayout()
        layout.addRow('Notation', self.cb_notation)

        self.setLayout(layout)

    def notation(self):
        return self.cb_notation.currentData(QtCore.Qt.UserRole)

    def setNotation(self, notation):
        index = self.cb_notation.findData(notation, QtCore.Qt.UserRole)
        self.cb_notation.setCurrentIndex(index)

class PreferredWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_units = PreferredUnitsWidget()

        self.wdg_xrayline = PreferredXrayLineWidget()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(create_group_box('Units', self.wdg_units))
        layout.addWidget(create_group_box('X-ray line', self.wdg_xrayline))
        self.setLayout(layout)

    def units(self):
        return self.wdg_units.units()

    def setUnits(self, units):
        self.wdg_units.setUnits(units)

    def xrayLineNotation(self):
        return self.wdg_xrayline.notation()

    def setXrayLineNotation(self, notation):
        self.wdg_xrayline.setNotation(notation)

class SettingsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_programs = ProgramsWidget()

        self.wdg_preferred = PreferredWidget()

        self.wdg_tab = QtWidgets.QTabWidget()
        self.wdg_tab.addTab(self.wdg_programs, 'Programs')
        self.wdg_tab.addTab(self.wdg_preferred, 'Preference')

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.wdg_tab)
        self.setLayout(layout)

    def settings(self):
        settings = Settings()

        settings.programs = self.wdg_programs.programs()

        settings.preferred_xrayline_notation = self.wdg_preferred.xrayLineNotation()

        settings.clear_preferred_units()
        for unit in self.wdg_preferred.units():
            settings.set_preferred_unit(unit)

        return settings

    def setSettings(self, settings):
        self.wdg_programs.setPrograms(settings.programs)

        self.wdg_preferred.setXrayLineNotation(settings.preferred_xrayline_notation)

        self.wdg_preferred.setUnits(settings.preferred_units.values())

class SettingsCentralWidget(QtWidgets.QWidget):

    saved = QtCore.Signal()
    aborted = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_settings = SettingsWidget()
        self.wdg_settings.layout().setContentsMargins(0, 0, 0, 0)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save |
                                             QtWidgets.QDialogButtonBox.Abort)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.wdg_settings)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # Signals
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.aborted)

    def _on_save(self):
        settings = self.settings()

        try:
            settings.validate()
        except ValidationError as ex:
            messagebox.exception(self, ex)
            return

        try:
            settings.write()
        except Exception as ex:
            messagebox.exception(self, ex)
            return

        message = 'Settings successfully saved'
        QtWidgets.QMessageBox.information(self, 'Save', message)

        self.saved.emit()

    def settings(self):
        return self.wdg_settings.settings()

    def setSettings(self, settings):
        self.wdg_settings.setSettings(settings)

class SettingsMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')

        # Widgets
        self.wdg_central = SettingsCentralWidget()

        # Layouts
        self.setCentralWidget(self.wdg_central)

        # Signals
        self.wdg_central.saved.connect(self.close)
        self.wdg_central.aborted.connect(self.close)

    def settings(self):
        return self.wdg_central.settings()

    def setSettings(self, settings):
        self.wdg_central.setSettings(settings)
