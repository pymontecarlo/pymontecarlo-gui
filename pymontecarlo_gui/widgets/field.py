""""""

# Standard library modules.
import abc
import functools

# Third party modules.
from qtpy import QtWidgets, QtCore, QtGui

# Local modules.
from pymontecarlo_gui.util.validate import Validable
from pymontecarlo_gui.util.metaclass import QABCMeta
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.widgets.font import make_italic
from pymontecarlo_gui.widgets.stacked import clear_stackedwidget

# Globals and constants variables.

class Field(QtCore.QObject, Validable, metaclass=QABCMeta):

    fieldChanged = QtCore.Signal()

    @abc.abstractmethod
    def title(self):
        return ''

    def titleLabel(self):
        label = QtWidgets.QLabel(self.title())
        label.setToolTip(self.description())
        return label

    def description(self):
        return ''

    def descriptionLabel(self):
        label = QtWidgets.QLabel(self.description())
        label.setWordWrap(True)
        make_italic(label)
        return label

    def hasDescription(self):
        return bool(self.description())

    @abc.abstractmethod
    def widget(self):
        return QtWidgets.QWidget()

    def suffix(self):
        return None

    def hasSuffix(self):
        return self.suffix() is not None

    def isValid(self):
        if not super().isValid():
            return False

        widget = self.widget()
        if isinstance(widget, Validable) and not widget.isValid():
            return False

        return True

class MultiValueField(Field):

    def titleLabel(self):
        label = super().titleLabel()
        label.setStyleSheet('color: blue')
        return label

class WidgetField(Field):

    def __init__(self):
        super().__init__()

        # Variables
        self._fields = []

        # Widgets
        self._widget = QtWidgets.QWidget()

        layout = FieldLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._widget.setLayout(layout)

    def _add_field(self, field):
        self._fields.append(field)
        field.fieldChanged.connect(self.fieldChanged)
        self._widget.adjustSize()

    def addLabelField(self, field):
        self._widget.layout().addLabelField(field)
        self._add_field(field)

    def addGroupField(self, field):
        self._widget.layout().addGroupField(field)
        self._add_field(field)

    def widget(self):
        return self._widget

    def isValid(self):
        return super().isValid() and \
            all(field.isValid() for field in self._fields)

class ToolBoxField(Field):

    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = FieldToolBox()

    def addField(self, field):
        self._widget.addField(field)
        field.fieldChanged.connect(self.fieldChanged)
        self._widget.adjustSize()

    def widget(self):
        return self._widget

class FieldLayout(QtWidgets.QVBoxLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.lyt_field = QtWidgets.QGridLayout()
        self.addLayout(self.lyt_field)
        self.addStretch()

    def addLabelField(self, field):
        row = self.lyt_field.rowCount()
        has_suffix = field.hasSuffix()

        # Label
        self.lyt_field.addWidget(field.titleLabel(), row, 0)

        # Widget
        colspan = 1 if has_suffix else 2
        self.lyt_field.addWidget(field.widget(), row, 1, 1, colspan)

        # Suffix
        if has_suffix:
            self.lyt_field.addWidget(field.suffix(), row, 2)

    def addGroupField(self, field):
        row = self.lyt_field.rowCount()
        has_description = field.hasDescription()
        has_suffix = field.hasSuffix()

        widgets = [field.widget()]
        if has_description:
            widgets.append(field.descriptionLabel())
        if has_suffix:
            widgets.append(field.suffix())

        groupbox = create_group_box(field.title(), *widgets)
        self.lyt_field.addWidget(groupbox, row, 0, 1, 3)

class FieldToolBox(QtWidgets.QToolBox, Validable):

    def _on_field_changed(self, index, field):
        if field.isValid():
            icon = QtGui.QIcon()
        else:
            icon = QtGui.QIcon.fromTheme("dialog-error")

        self.setItemIcon(index, icon)

    def isValid(self):
        for index in range(self.count()):
            widget = self.widget(index)
            if not isinstance(widget, Validable):
                continue
            if not widget.isValid():
                return False

        return super().isValid()

    def addField(self, field):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        if field.hasDescription():
            layout.addWidget(field.descriptionLabel())
        if field.hasSuffix():
            layout.addWidget(field.suffix())
        layout.addWidget(field.widget())

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        index = self.addItem(widget, field.title())

        field.fieldChanged.connect(functools.partial(self._on_field_changed, index, field))

        return index

class FieldChooser(QtWidgets.QWidget):

    currentFieldChanged = QtCore.Signal(Field)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._fields = []

        # Widgets
        self.combobox = QtWidgets.QComboBox()

        self.lbl_description = QtWidgets.QLabel()
        make_italic(self.lbl_description)
        self.lbl_description.setWordWrap(True)

        self.widget = QtWidgets.QStackedWidget()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combobox)
        layout.addWidget(self.lbl_description)
        layout.addWidget(self.widget)
        self.setLayout(layout)

        # Signals
        self.combobox.currentIndexChanged.connect(self._on_index_changed)

    def _on_index_changed(self, index):
        widget_index = self.combobox.itemData(index)
        self.widget.setCurrentIndex(widget_index)

        print(index)
        field = self._fields[index]
        self.lbl_description.setText(field.description())

        self.currentFieldChanged.emit(field)

    def addField(self, field):
        self._fields.append(field)
        widget_index = self.widget.addWidget(field.widget())
        self.combobox.addItem(field.title(), widget_index)

        if self.combobox.count() == 1:
            self.combobox.setCurrentIndex(0)

    def removeField(self, field):
        if field not in self._fields:
            return

        index = self._fields.index(field)
        widget_index = self.combobox.itemData(index)
        widget = self.widget.widget(widget_index)

        self.combobox.removeItem(index)
        self.widget.removeWidget(widget)
        self._fields.remove(field)

    def clear(self):
        self.combobox.clear()
        clear_stackedwidget(self.widget)
        self._fields.clear()

    def currentField(self):
        index = self.combobox.currentIndex()
        if index < 0:
            return None
        return self._fields[index]
