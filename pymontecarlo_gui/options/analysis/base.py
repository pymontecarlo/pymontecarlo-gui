""""""

# Standard library modules.
import abc

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.util.validate import Validable
from pymontecarlo_gui.widgets.field import Field, FieldToolBox
from pymontecarlo_gui.options.detector.photon import PhotonDetectorWidget

# Globals and constants variables.

class PhotonDetectorField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._label = QtWidgets.QLabel('Photon detector(s)')

        self._widget = PhotonDetectorWidget()

        # Signals
        self._widget.changed.connect(self.changed)

    def label(self):
        return self._label

    def widget(self):
        return self._widget

    def detectors(self):
        return self._widget.detectors()

class AnalysisToolBox(QtWidgets.QWidget, Validable):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._registered_requirements = {}
        self._toolbox_indexes = {}

        # Fields
        self.field_photon_detector = PhotonDetectorField()

        # Widgets
        self.toolbox = FieldToolBox()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbox)
        self.setLayout(layout)

        # Signals
        self.field_photon_detector.changed.connect(self.changed)

    def _registerRequirement(self, analysis, field):
        if not self._registered_requirements.get(field, None):
            index = self.toolbox.addGroupField(field)
            self._toolbox_indexes[field] = index

        self._registered_requirements.setdefault(field, set()).add(analysis)

        self.changed.emit()

    def _unregisterRequirement(self, analysis, field):
        if field not in self._registered_requirements:
            return

        self._registered_requirements[field].remove(analysis)

        if not self._registered_requirements[field]:
            index = self._toolbox_indexes.pop(field)
            self.toolbox.removeItem(index)

        self.changed.emit()

    def isValid(self):
        return super().isValid() and self.toolbox.isValid()

    def registerPhotonDetectorRequirement(self, analysis):
        self._registerRequirement(analysis, self.field_photon_detector)

    def unregisterPhotonDetectorRequirement(self, analysis):
        self._unregisterRequirement(analysis, self.field_photon_detector)

    def photonDetectors(self):
        return self.field_photon_detector.detectors()

class AnalysisWidget(QtWidgets.QWidget, Validable, metaclass=QABCMeta):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._toolbox = None

        # Widgets
        self.checkbox = QtWidgets.QCheckBox()

        self.lbl_name = QtWidgets.QLabel(self.accessibleName())
        self.lbl_name.setWordWrap(True)

        self.lbl_description = QtWidgets.QLabel(self.accessibleDescription())
        self.lbl_description.setWordWrap(True)
        font = self.lbl_description.font()
        font.setItalic(True)
        self.lbl_description.setFont(font)

        # Layouts
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.checkbox, 0, 0)
        layout.addWidget(self.lbl_name, 0, 1, QtCore.Qt.AlignLeft)
        layout.addWidget(self.lbl_description, 1, 1, QtCore.Qt.AlignLeft)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)

        # Signals
        self.checkbox.stateChanged.connect(self._on_checked)

    def _on_checked(self):
        if self._toolbox:
            if self.checkbox.isChecked():
                self._register_requirements(self._toolbox)
            else:
                self._unregister_requirements(self._toolbox)

        self.changed.emit()

    def _register_requirements(self, toolbox):
        pass

    def _unregister_requirements(self, toolbox):
        pass

    def setAccessibleName(self, name):
        super().setAccessibleName(name)
        self.lbl_name.setText(name)

    def setAccessibleDescription(self, description):
        super().setAccessibleDescription(description)
        self.lbl_description.setText(description)

    def isValid(self):
        return super().isValid()

    def isSelected(self):
        return self.checkbox.isChecked()

    def setSelection(self, selected):
        self.checkbox.setChecked(selected)

    def analysisToolBox(self):
        return self._toolbox

    def setAnalysisToolBox(self, toolbox):
        self._toolbox = toolbox

    @abc.abstractmethod
    def analyses(self):
        return []

class AnalysesWidget(QtWidgets.QWidget, Validable):

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._widgets = []
        self._toolbox = None

        # Widgets
        self.scrollarea = QtWidgets.QScrollArea()
        self.scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollarea.setLineWidth(0)
        self.scrollarea.setFrameStyle(QtWidgets.QFrame.Plain)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollarea)
        self.setLayout(layout)

    def isValid(self):
        selection = [widget for widget in self._widgets if widget.isSelected()]
        if not selection:
            return False

        for widget in selection:
            if not widget.isValid():
                return False

        return super().isValid()

    def addAnalysisWidget(self, analysis_widget):
        analysis_widget.setAnalysisToolBox(self.analysisToolBox())
        self._widgets.append(analysis_widget)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for widget in self._widgets:
            layout.addWidget(widget)
        layout.addStretch()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.scrollarea.setWidget(widget)

        # Signals
        analysis_widget.changed.connect(self.changed)

    def analysisToolBox(self):
        return self._toolbox

    def setAnalysisToolBox(self, toolbox):
        self._toolbox = toolbox
        for widget in self._widgets:
            widget.setAnalysisToolBox(toolbox)

    def analyses(self):
        analyses = []

        for widget in self._widgets:
            if not widget.isSelected():
                continue
            analyses.extend(widget.analyses())

        return analyses
