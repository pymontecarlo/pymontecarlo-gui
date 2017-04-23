""""""

# Standard library modules.
import textwrap

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

import pandas as pd

# Local modules.
from pymontecarlo_gui.results.base import ResultSummaryWidget
from pymontecarlo_gui.widgets.groupbox import create_group_box

# Globals and constants variables.

class ResultSummaryModel(QtCore.QAbstractTableModel):

    def __init__(self, textwidth, project=None):
        super().__init__()

        # Variables
        self._textwidth = textwidth

        self._project = project
        self._result_classes = []
        self._only_different_options = False

        self._df = pd.DataFrame()
        self._column_width = 100

        self._update_dataframe()

    def _update_dataframe(self):
        self._df = pd.DataFrame()

        if self._project is None:
            return

        df_options = \
            self._project.create_options_dataframe(self._only_different_options)
        df_results = \
            self._project.create_results_dataframe(self._result_classes)

        self._df = pd.concat([df_options, df_results], axis=1)

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
            columnobj = self._df.columns[column]
            return columnobj.format_value(value)

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            text = self._df.columns[section].fullname
            return '\n'.join(textwrap.wrap(text, self._textwidth))

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
        self.update()

    def resultClasses(self):
        return self._result_classes

    def setResultClasses(self, result_classes):
        self._result_classes = set(result_classes)
        self.update()

    def isOnlyDifferentOptions(self):
        return self._only_different_options

    def setOnlyDifferentOptions(self, answer):
        self._only_different_options = answer
        self.update()

    def setColumnWidth(self, width):
        self._column_width = width
        self.layoutChanged.emit()

    def toList(self, include_header=True):
        out = []

        if include_header:
            out.append(self._columns)

        for row in self._rows:
            out.append([row.get(key, float('nan')) for key in self._columns])

        return out

    def update(self):
        self._update_dataframe()
        self.modelReset.emit()

class ResultClassListWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_list = QtWidgets.QListWidget()

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.act_selectall = self.toolbar.addAction('Select all')
        self.act_unselectall = self.toolbar.addAction('Unselect all')

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.wdg_list)
        layout.addWidget(self.toolbar, 0, QtCore.Qt.AlignRight)
        self.setLayout(layout)

        # Signals
        self.wdg_list.itemChanged.connect(self._on_list_item_changed)
        self.act_selectall.triggered.connect(self._on_selectall)
        self.act_unselectall.triggered.connect(self._on_unselectall)

    def _on_list_item_changed(self, item):
        self._update_toolbar()
        self.selectionChanged.emit()

    def _on_selectall(self):
        for index in range(self.wdg_list.count()):
            item = self.wdg_list.item(index)
            item.setCheckState(QtCore.Qt.Checked)

        self._update_toolbar()

    def _on_unselectall(self):
        for index in range(self.wdg_list.count()):
            item = self.wdg_list.item(index)
            item.setCheckState(QtCore.Qt.Unchecked)

        self._update_toolbar()

    def _update_toolbar(self):
        rows = self.wdg_list.count()
        has_rows = rows > 0
        checked = sum(self.wdg_list.item(index).checkState() == QtCore.Qt.Checked
                      for index in range(self.wdg_list.count()))

        self.act_selectall.setEnabled(has_rows and checked < rows)
        self.act_unselectall.setEnabled(has_rows and checked > 0)

    def setProject(self, project):
        self.setResultClasses(project.result_classes)

    def resultClasses(self):
        classes = []

        for index in range(self.wdg_list.count()):
            item = self.wdg_list.item(index)
            if item.checkState() != QtCore.Qt.Checked:
                continue
            classes.append(item.data(QtCore.Qt.UserRole))

        return classes

    def setResultClasses(self, classes):
        self.wdg_list.clear()

        for clasz in classes:
            name = clasz.getname()
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, clasz)
            item.setTextAlignment(QtCore.Qt.AlignLeft)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.wdg_list.addItem(item)

        self._update_toolbar()

class ResultSummaryTableWidget(ResultSummaryWidget):

    COLUMN_WIDTH = 125

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.wdg_table = QtWidgets.QTableView()

        header = self.wdg_table.verticalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        header = self.wdg_table.horizontalHeader()
        header.setDefaultSectionSize(self.COLUMN_WIDTH)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        textwidth = int(self.COLUMN_WIDTH / header.fontMetrics().width('a'))
        model = ResultSummaryModel(textwidth)
        self.wdg_table.setModel(model)

        self.chk_diff_options = QtWidgets.QCheckBox("Only different columns")

        self.lst_results = ResultClassListWidget()

        self.tlb_export = QtWidgets.QToolBar()
        self.tlb_export.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.act_copy = self.tlb_export.addAction(QtGui.QIcon.fromTheme('edit-copy'), 'Copy')
        #self.act_save = self.tlb_export.addAction(QtGui.QIcon.fromTheme('document-save'), 'CSV')

        # Layouts
        lyt_right = QtWidgets.QVBoxLayout()
        lyt_right.addWidget(create_group_box('Options', self.chk_diff_options))
        lyt_right.addWidget(create_group_box('Results', self.lst_results))
        lyt_right.addWidget(create_group_box('Export', self.tlb_export))

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.wdg_table, 3)
        layout.addLayout(lyt_right, 1)
        self.setLayout(layout)

        # Signals
        self.chk_diff_options.stateChanged.connect(self._on_diff_options_changed)

        self.lst_results.selectionChanged.connect(self._on_result_class_changed)

        self.act_copy.triggered.connect(self._on_copy)
        #self.act_save.triggered.connect(self._on_save)

    def _on_diff_options_changed(self, state):
        answer = state == QtCore.Qt.Checked
        self.wdg_table.model().setOnlyDifferentOptions(answer)

    def _on_result_class_changed(self):
        result_classes = self.lst_results.resultClasses()
        self.wdg_table.model().setResultClasses(result_classes)

    def _on_copy(self):
        rows = self.wdg_table.model().toList()
        text = '\n'.join('\t'.join(map(str, row)) for row in rows)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

#    def _on_save(self):
#        pass

    def setProject(self, project):
        self.wdg_table.model().setProject(project)
        self.lst_results.setProject(project)

    def update(self, *args):
        self.wdg_table.model().update()
        super().update()

def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    from pymontecarlo.testcase import TestCase
    TestCase.setUpClass()
    testcase = TestCase()
    testcase.setUp()
    project = testcase.create_basic_project()

    import pymontecarlo
    pymontecarlo.settings.set_preferred_unit('eV')
    pymontecarlo.settings.set_preferred_unit('nm')

    widget = ResultSummaryTableWidget()
    widget.setProject(project)

    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(widget)
    mainwindow.show()

    app.exec_()

if __name__ == '__main__':
    run()
