""""""

# Standard library modules.
import functools
import traceback

# Third party modules.
from qtpy import QtWidgets, QtCore, QtGui

import pygments
from pygments.lexers.python import Python3Lexer
from pygments.formatters.html import HtmlFormatter

# Local modules.
from pymontecarlo_gui.util.validate import ValidableBase
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.widgets.font import make_italic
from pymontecarlo_gui.widgets.stacked import clear_stackedwidget
from pymontecarlo_gui.widgets.mdi import MdiSubWindow

# Globals and constants variables.


class FieldBase(QtCore.QObject, ValidableBase):

    fieldChanged = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.wdg_title = QtWidgets.QLabel(self.title())
        self.wdg_title.setToolTip(self.description())

        self.wdg_description = QtWidgets.QLabel(self.description())
        self.wdg_description.setWordWrap(True)
        make_italic(self.wdg_description)

    def title(self):
        return ""

    def titleWidget(self):
        return self.wdg_title

    def description(self):
        return ""

    def descriptionWidget(self):
        return self.wdg_description

    def hasDescription(self):
        return bool(self.description())

    def icon(self):
        return QtGui.QIcon()

    def widget(self):
        return QtWidgets.QWidget()

    def suffixWidget(self):
        return None

    def hasSuffix(self):
        return self.suffixWidget() is not None

    def isValid(self):
        if not super().isValid():
            return False

        widget = self.widget()
        if isinstance(widget, ValidableBase) and not widget.isValid():
            return False

        return True

    def isEnabled(self):
        return self.widget().isEnabled()

    def setEnabled(self, enabled):
        self.titleWidget().setEnabled(enabled)
        self.descriptionWidget().setEnabled(enabled)
        self.widget().setEnabled(enabled)
        if self.hasSuffix():
            self.suffixWidget().setEnabled(enabled)


class MultiValueFieldBase(FieldBase):
    def titleWidget(self):
        label = super().titleWidget()
        label.setStyleSheet("color: blue")
        return label

    def setEnabled(self, enabled):
        super().setEnabled(enabled)

        label = super().titleWidget()
        label.setStyleSheet("color: blue" if enabled else "color: #7e7d8d")


class CheckFieldBase(FieldBase):
    def __init__(self):
        super().__init__()

        self.wdg_title = QtWidgets.QCheckBox(self.title())
        self.wdg_title.setToolTip(self.description())
        self.wdg_title.stateChanged.connect(self.fieldChanged)

    def isChecked(self):
        return self.titleWidget().isChecked()

    def setChecked(self, checked):
        self.titleWidget().setChecked(checked)

    def widget(self):
        return QtWidgets.QWidget()


class WidgetFieldBase(FieldBase):
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

    def addCheckField(self, field):
        self._widget.layout().addCheckField(field)
        self._add_field(field)

    def widget(self):
        return self._widget

    def isValid(self):
        return super().isValid() and all(field.isValid() for field in self._fields)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)

        for field in self._fields:
            field.setEnabled(enabled)

    def fields(self):
        return tuple(self._fields)


class ToolBoxFieldBase(FieldBase):
    def __init__(self):
        super().__init__()

        # Widgets
        self._widget = FieldToolBox()

    def addField(self, field):
        self._widget.addField(field)
        field.fieldChanged.connect(self.fieldChanged)

    def removeField(self, field):
        self._widget.removeField(field)
        field.fieldChanged.disconnect(self.fieldChanged)

    def widget(self):
        return self._widget


class ExceptionField(FieldBase):
    def __init__(self, exception):
        self._exception = exception
        super().__init__()

        stack = traceback.extract_tb(exception.__traceback__)
        summary = traceback.StackSummary.from_list(stack)
        lines = summary.format()
        code = "".join(lines)

        lexer = Python3Lexer()
        formatter = HtmlFormatter(full=True)
        text = pygments.highlight(code, lexer, formatter)

        # Widgets
        self._widget = QtWidgets.QTextEdit()
        self._widget.setReadOnly(True)
        self._widget.setFont(
            QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        )
        self._widget.setHtml(text)

    def title(self):
        return str(self.exception())

    def icon(self):
        return QtGui.QIcon.fromTheme("dialog-error")

    def widget(self):
        return self._widget

    def exception(self):
        return self._exception


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
        self.lyt_field.addWidget(field.titleWidget(), row, 0)

        # Widget
        colspan = 1 if has_suffix else 2
        self.lyt_field.addWidget(field.widget(), row, 1, 1, colspan)

        # Suffix
        if has_suffix:
            self.lyt_field.addWidget(field.suffixWidget(), row, 2)

    def addGroupField(self, field):
        row = self.lyt_field.rowCount()
        has_description = field.hasDescription()
        has_suffix = field.hasSuffix()

        widgets = []
        if has_description:
            widgets.append(field.descriptionWidget())

        widgets.append(field.widget())

        if has_suffix:
            widgets.append(field.suffixWidget())

        groupbox = create_group_box(field.title(), *widgets)
        self.lyt_field.addWidget(groupbox, row, 0, 1, 3)

    def addCheckField(self, field):
        row = self.lyt_field.rowCount()
        has_description = field.hasDescription()
        has_suffix = field.hasSuffix()

        self.lyt_field.addWidget(field.titleWidget(), row, 0, 1, 3)
        row += 1

        if has_description:
            self.lyt_field.addWidget(field.descriptionWidget(), row, 0, 1, 3)
            row += 1

        self.lyt_field.addWidget(field.widget(), row, 0, 1, 3)
        row += 1

        if has_suffix:
            self.lyt_field.addWidget(field.suffixWidget(), row, 0, 1, 3)


class FieldToolBox(QtWidgets.QToolBox, ValidableBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._fields = {}

    def _on_field_changed(self):
        field = self.sender()
        if field not in self._fields:
            return

        index = self._fields[field]

        if field.isValid():
            icon = QtGui.QIcon()
        else:
            icon = QtGui.QIcon.fromTheme("dialog-error")

        self.setItemIcon(index, icon)

    def isValid(self):
        for field in self._fields:
            if not field.isValid():
                return False
        return super().isValid()

    def addField(self, field, enabled=True):
        if field in self._fields:
            raise ValueError('FieldBase "{}" already added'.format(field))

        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        if field.hasDescription():
            layout.addWidget(field.descriptionWidget())

            frame = QtWidgets.QFrame()
            frame.setFrameShape(QtWidgets.QFrame.HLine)
            frame.setFrameShadow(QtWidgets.QFrame.Sunken)
            layout.addWidget(frame)

        if field.hasSuffix():
            layout.addWidget(field.suffixWidget())

        layout.addWidget(field.widget())

        # Create and add widget
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        index = self.addItem(widget, field.title())
        self._fields[field] = index

        self.setItemEnabled(index, enabled)
        field.setEnabled(enabled)

        field.fieldChanged.connect(self._on_field_changed)

        return index

    def removeField(self, field):
        if field not in self._fields:
            raise ValueError('FieldBase "{}" unknown'.format(field))

        index = self._fields.pop(field)
        self.removeItem(index)

        field.fieldChanged.disconnect(self._on_field_changed)

    def setSelectedFields(self, fields):
        for field, index in self._fields.items():
            if field not in fields:
                self.setItemEnabled(index, False)
                field.setEnabled(False)
            elif not field.isEnabled():
                self.setItemEnabled(index, True)
                field.setEnabled(True)
                self.setCurrentIndex(index)

    def fields(self):
        return tuple(self._fields.keys())


class FieldChooser(QtWidgets.QWidget):

    currentFieldChanged = QtCore.Signal(FieldBase)

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

        field = self._fields[index]
        description = field.description()
        self.lbl_description.setText(description)
        self.lbl_description.setVisible(bool(description))

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

    def fields(self):
        return tuple(self._fields)


class FieldTree(QtWidgets.QWidget):

    doubleClicked = QtCore.Signal(FieldBase)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._field_items = {}

        # Widgets
        self.tree = QtWidgets.QTreeWidget()
        self.tree.header().close()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)
        self.setLayout(layout)

        # Signals
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_item_double_clicked(self, item):
        field = item.data(0, QtCore.Qt.UserRole)
        self.doubleClicked.emit(field)

    def addField(self, field, parent_field=None):
        if field in self._field_items:
            raise ValueError("FieldBase {} already in tree".format(field))

        if parent_field is None:
            parent_field = self.tree
        else:
            parent_field = self._field_items[parent_field]

        item = QtWidgets.QTreeWidgetItem(parent_field)
        item.setText(0, field.title())
        item.setToolTip(0, field.description())
        item.setIcon(0, field.icon())
        item.setData(0, QtCore.Qt.UserRole, field)

        self._field_items[field] = item

    def removeField(self, field):
        if field not in self._field_items:
            raise ValueError("FieldBase {} is not part of the tree".format(field))

        item = self._field_items.pop(field)
        item.parent().removeChild(item)

    def clear(self):
        self._field_items.clear()
        self.tree.clear()

    def containField(self, field):
        return field in self._field_items

    def expandField(self, field):
        if field not in self._field_items:
            raise ValueError("FieldBase {} is not part of the tree".format(field))
        item = self._field_items[field]
        self.tree.expandItem(item)

    def expand(self):
        self.tree.expandAll()

    def collapseField(self, field):
        if field not in self._field_items:
            raise ValueError("FieldBase {} is not part of the tree".format(field))
        item = self._field_items[field]
        self.tree.collapseItem(item)

    def collapse(self):
        self.tree.collapseAll()

    def setFieldFont(self, field, font):
        if field not in self._field_items:
            raise ValueError("FieldBase {} is not part of the tree".format(field))
        item = self._field_items[field]
        item.setFont(0, font)

    def fieldFont(self, field):
        if field not in self._field_items:
            raise ValueError("FieldBase {} is not part of the tree".format(field))
        item = self._field_items[field]
        return item.font(0)

    def topLevelFields(self):
        fields = []

        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            fields.append(item.data(0, QtCore.Qt.UserRole))

        return fields

    def childrenField(self, field):
        if field not in self._field_items:
            raise ValueError("FieldBase {} is not part of the tree".format(field))
        item = self._field_items[field]

        children = []
        for index in range(item.childCount()):
            childitem = item.child(index)
            children.append(childitem.data(0, QtCore.Qt.UserRole))

        return children

    def reset(self):
        for field, item in self._field_items.items():
            item.setText(0, field.title())
            item.setToolTip(0, field.description())
            item.setIcon(0, field.icon())

        self.tree.reset()

    def resetField(self, field):
        if field not in self._field_items:
            raise ValueError("FieldBase {} is not part of the tree".format(field))
        item = self._field_items[field]
        item.setText(0, field.title())
        item.setToolTip(0, field.description())
        item.setIcon(0, field.icon())


class FieldMdiArea(QtWidgets.QWidget):

    windowOpened = QtCore.Signal(FieldBase)
    windowClosed = QtCore.Signal(FieldBase)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._field_windows = {}

        # Widgets
        self.mdiarea = QtWidgets.QMdiArea()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mdiarea)
        self.setLayout(layout)

    def _on_window_closed(self, field):
        if field in self._field_windows:
            field.widget().setParent(None)
            self._field_windows.pop(field)
            self.windowClosed.emit(field)

    def addField(self, field):
        if field in self._field_windows:
            window = self._field_windows[field]
        else:
            window = MdiSubWindow()
            window.setWindowTitle(field.title())
            window.setWindowIcon(field.icon())
            window.setWidget(field.widget())
            window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            window.closed.connect(functools.partial(self._on_window_closed, field))

            self._field_windows[field] = window

        if window in self.mdiarea.subWindowList():
            self.mdiarea.setActiveSubWindow(window)
        else:
            self.mdiarea.addSubWindow(window)

        window.showNormal()
        window.raise_()
        self.windowOpened.emit(field)

    def removeField(self, field):
        if field not in self._field_windows:
            return

        window = self._field_windows.pop(field)
        self.mdiarea.removeSubWindow(window)

    def clear(self):
        self._field_windows.clear()
        self.mdiarea.closeAllSubWindows()
