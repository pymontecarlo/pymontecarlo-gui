""""""

# Standard library modules.
import textwrap
import operator
from numbers import Number

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

import pandas as pd

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT,
)

# Local modules.
from pymontecarlo.util.human import camelcase_to_words

from pymontecarlo_gui.results.base import ResultSummaryWidgetBase
from pymontecarlo_gui.widgets.groupbox import create_group_box
from pymontecarlo_gui.widgets.list import CheckListToolBar, SelectionListToolBar

# Globals and constants variables.


class ResultSummaryTableModel(QtCore.QAbstractTableModel):
    def __init__(self, settings, textwidth, project=None):
        super().__init__()

        # Variables
        self._settings = settings
        self._textwidth = textwidth

        self._project = project
        self._result_classes = []
        self._only_different_options = False

        self._df = pd.DataFrame()
        self._column_width = 100

        self._update_dataframe()

        # Signals
        settings.settings_changed.connect(self._on_settings_changed)

    def _on_settings_changed(self):
        self._update_dataframe()

    def _update_dataframe(self):
        if self._project is None:
            self._df = pd.DataFrame()
            return

        df_options = self._project.create_options_dataframe(
            self._settings, False, format_number=True
        )

        if self._only_different_options:
            columns = self._project.create_options_dataframe(
                self._settings, True
            ).columns
            df_options = df_options[columns]

        df_results = self._project.create_results_dataframe(
            self._settings, self._result_classes, format_number=True
        )

        self._df = pd.concat([df_options, df_results], axis=1)

        self.modelReset.emit()

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if row < 0 or row >= len(self._df):
            return None

        if role == QtCore.Qt.DisplayRole:
            value = self._df.iloc[row, column]
            return value

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            text = self._df.columns[section]
            return "\n".join(textwrap.wrap(text, self._textwidth))

        elif orientation == QtCore.Qt.Vertical:
            return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(super().flags(index))

    def project(self, project):
        return self._project

    def setProject(self, project):
        self._project = project
        self._update_dataframe()

    def resultClasses(self):
        return self._result_classes

    def setResultClasses(self, result_classes):
        self._result_classes = set(result_classes)
        self._update_dataframe()

    def isOnlyDifferentOptions(self):
        return self._only_different_options

    def setOnlyDifferentOptions(self, answer):
        self._only_different_options = answer
        self._update_dataframe()

    def setColumnWidth(self, width):
        self._column_width = width
        self.layoutChanged.emit()

    def toList(self, include_header=True):
        out = []

        if include_header:
            out.append([column for column in self._df.columns])

        for _index, series in self._df.iterrows():
            row = []
            for column, value in series.iteritems():
                row.append(value)
            out.append(row)

        return out


class ResultClassListWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.listwidget = QtWidgets.QListWidget()

        self.toolbar_columns = CheckListToolBar()
        self.toolbar_columns.setListWidget(self.listwidget)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.listwidget)
        layout.addWidget(self.toolbar_columns, 0, QtCore.Qt.AlignRight)
        self.setLayout(layout)

        # Signals
        self.listwidget.itemChanged.connect(self.selectionChanged)

    def setProject(self, project):
        self.setResultClasses(project.result_classes)

    def resultClasses(self):
        classes = []

        for index in range(self.listwidget.count()):
            item = self.listwidget.item(index)
            if item.checkState() != QtCore.Qt.Checked:
                continue
            classes.append(item.data(QtCore.Qt.UserRole))

        return classes

    def setResultClasses(self, classes):
        self.listwidget.clear()

        for clasz in classes:
            name = clasz.getname()
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, clasz)
            item.setTextAlignment(QtCore.Qt.AlignLeft)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.listwidget.addItem(item)


class ResultSummaryTableWidget(ResultSummaryWidgetBase):

    COLUMN_WIDTH = 125

    def __init__(self, settings, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_table = QtWidgets.QTableView()

        header = self.wdg_table.verticalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        header = self.wdg_table.horizontalHeader()
        header.setDefaultSectionSize(self.COLUMN_WIDTH)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        textwidth = int(self.COLUMN_WIDTH / header.fontMetrics().width("a"))
        model = ResultSummaryTableModel(settings, textwidth)
        self.wdg_table.setModel(model)

        self.chk_diff_options = QtWidgets.QCheckBox("Only different columns")

        self.lst_results = ResultClassListWidget()

        self.tlb_export = QtWidgets.QToolBar()
        self.tlb_export.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.act_copy = self.tlb_export.addAction(
            QtGui.QIcon.fromTheme("edit-copy"), "Copy"
        )
        # self.act_save = self.tlb_export.addAction(QtGui.QIcon.fromTheme('document-save'), 'CSV')

        # Layouts
        lyt_right = QtWidgets.QVBoxLayout()
        lyt_right.addWidget(create_group_box("Options", self.chk_diff_options))
        lyt_right.addWidget(create_group_box("Results", self.lst_results))
        lyt_right.addWidget(create_group_box("Export", self.tlb_export))

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.wdg_table, 3)
        layout.addLayout(lyt_right, 1)
        self.setLayout(layout)

        # Signals
        self.chk_diff_options.stateChanged.connect(self._on_diff_options_changed)

        self.lst_results.selectionChanged.connect(self._on_result_class_changed)

        self.act_copy.triggered.connect(self._on_copy)
        # self.act_save.triggered.connect(self._on_save)

    def _on_diff_options_changed(self, state):
        answer = state == QtCore.Qt.Checked
        self.wdg_table.model().setOnlyDifferentOptions(answer)

    def _on_result_class_changed(self):
        result_classes = self.lst_results.resultClasses()
        self.wdg_table.model().setResultClasses(result_classes)

    def _on_copy(self):
        rows = self.wdg_table.model().toList()
        text = "\n".join("\t".join(map(str, row)) for row in rows)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

    #    def _on_save(self):
    #        pass

    def setProject(self, project):
        self.wdg_table.model().setProject(project)
        self.lst_results.setProject(project)


class ResultSummaryFigureWidget(ResultSummaryWidgetBase):
    def __init__(self, settings, parent=None):
        super().__init__(parent)

        # Variables
        self._settings = settings
        self._project = None

        # Widgets
        fig = Figure()
        self.canvas = FigureCanvas(fig)

        self.toolbar_canvas = NavigationToolbar2QT(self.canvas, self)

        self.combobox_xaxis = QtWidgets.QComboBox()

        self.combobox_yaxis = QtWidgets.QComboBox()

        self.list_columns = QtWidgets.QListWidget()

        self.toolbar_columns = CheckListToolBar()
        self.toolbar_columns.setListWidget(self.list_columns)

        self.checkbox_error = QtWidgets.QCheckBox("Show error columns")

        self.list_simulations = QtWidgets.QListWidget()
        self.list_simulations.setSelectionBehavior(QtWidgets.QListWidget.SelectRows)
        self.list_simulations.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        self.toolbar_simulations = SelectionListToolBar()
        self.toolbar_simulations.setListWidget(self.list_simulations)

        # Layouts
        layout_left = QtWidgets.QVBoxLayout()
        layout_left.addWidget(self.canvas)
        layout_left.addWidget(self.toolbar_canvas)

        layout_yaxis = QtWidgets.QVBoxLayout()
        layout_yaxis.addWidget(self.combobox_yaxis)
        layout_yaxis.addWidget(self.list_columns)
        layout_yaxis.addWidget(self.toolbar_columns, alignment=QtCore.Qt.AlignRight)
        layout_yaxis.addWidget(self.checkbox_error, alignment=QtCore.Qt.AlignRight)

        layout_simulations = QtWidgets.QVBoxLayout()
        layout_simulations.addWidget(self.list_simulations)
        layout_simulations.addWidget(
            self.toolbar_simulations, alignment=QtCore.Qt.AlignRight
        )

        layout_right = QtWidgets.QVBoxLayout()
        layout_right.addWidget(create_group_box("X axis", self.combobox_xaxis))
        layout_right.addWidget(create_group_box("Y axis", layout_yaxis))
        layout_right.addWidget(create_group_box("Simulations", layout_simulations))

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_left)
        layout.addLayout(layout_right)
        self.setLayout(layout)

        # Signals
        self.combobox_xaxis.currentIndexChanged.connect(self._on_xaxis_changed)

        self.combobox_yaxis.currentIndexChanged.connect(self._on_yaxis_changed)

        self.list_columns.itemChanged.connect(self._on_columns_changed)

        self.checkbox_error.stateChanged.connect(self._on_error_checked)

        self.list_simulations.itemSelectionChanged.connect(self._on_simulations_changed)

        settings.settings_changed.connect(self._on_settings_changed)

    def _on_xaxis_changed(self):
        self.draw()

    def _on_yaxis_changed(self):
        self._update_yaxis()
        self.draw()

    def _on_columns_changed(self):
        self.draw()

    def _on_simulations_changed(self):
        self.draw()

    def _on_error_checked(self):
        self._update_yaxis()
        self.draw()

    def _on_settings_changed(self):
        self.setProject(self._project)
        self.draw()

    def _update_yaxis(self):
        df = self.combobox_yaxis.currentData()
        if df is None:
            return

        self.list_columns.clear()

        for column in df.columns:
            if column.startswith("\u03C3(") and not self.checkbox_error.isChecked():
                continue

            item = QtWidgets.QListWidgetItem(column)
            item.setData(QtCore.Qt.UserRole, df[column])
            item.setTextAlignment(QtCore.Qt.AlignLeft)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.list_columns.addItem(item)

    def setProject(self, project):
        # Clear
        self.combobox_xaxis.clear()
        self.combobox_yaxis.clear()
        self.list_columns.clear()
        self.list_simulations.clear()
        self.canvas.figure.clear()

        self._project = project

        if project is None:
            return

        # X axis
        df = project.create_options_dataframe(
            self._settings, only_different_columns=True
        )
        for column in df.columns:
            self.combobox_xaxis.addItem(column, df[column])

        # Y axis
        for result_class in sorted(project.result_classes, key=lambda c: c.__name__):
            text = camelcase_to_words(result_class.__name__[:-6]).lower()
            df = project.create_results_dataframe(self._settings, [result_class])
            self.combobox_yaxis.addItem(text, df)

        # Simulations
        for index in range(len(project.simulations)):
            item = QtWidgets.QListWidgetItem("Simulation #{:d}".format(index))
            item.setTextAlignment(QtCore.Qt.AlignLeft)
            self.list_simulations.addItem(item)

        self.list_simulations.selectAll()

    def project(self):
        return self._project

    def draw(self):
        # Clear
        try:
            self.canvas.figure.clear()
        except:
            self.canvas.draw()
            return

        # X axis
        series_x = self.combobox_xaxis.currentData()

        # Y axis
        list_series_y = []
        for index in range(self.list_columns.count()):
            item = self.list_columns.item(index)
            if item.checkState() != QtCore.Qt.Checked:
                continue
            list_series_y.append(item.data(QtCore.Qt.UserRole))

        # Simulations
        indexes = []
        for index in range(self.list_simulations.count()):
            item = self.list_simulations.item(index)
            if item.isSelected():
                indexes.append(index)

        # Plot
        fig = self.canvas.figure
        ax = fig.add_subplot(111)

        # Lines
        if series_x is not None and list_series_y:
            for series_y in list_series_y:
                data = []
                for index, (x, y) in enumerate(zip(series_x.values, series_y.values)):
                    if index not in indexes:
                        continue
                    if not isinstance(x, Number) or not isinstance(y, Number):
                        continue
                    if np.isnan(x) or np.isnan(y):
                        continue
                    data.append([x, y])

                data.sort(key=operator.itemgetter(0))
                xs = list(map(operator.itemgetter(0), data))
                ys = list(map(operator.itemgetter(1), data))

                label = series_y.name
                ax.plot(xs, ys, "o-", label=label)

        # Axes label
        if series_x is not None:
            ax.set_xlabel(series_x.name)

        if len(list_series_y) == 1:
            resultname = self.combobox_yaxis.currentText()
            series_y = list_series_y[0]
            ax.set_ylabel("{} {}".format(resultname, series_y.name))
        elif len(list_series_y) > 1:
            resultname = self.combobox_yaxis.currentText()
            ax.set_ylabel("{}".format(resultname))

        if len(list_series_y) > 1:
            ax.legend(loc="best")

        self.canvas.draw()
