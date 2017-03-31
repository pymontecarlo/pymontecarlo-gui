""""""

# Standard library modules.
import operator
import functools

# Third party modules.
from qtpy import QtCore, QtWidgets
from matplotlib import figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
import matplotlib.pyplot as plt

# Local modules.
from pymontecarlo_gui.results.base import ResultSummaryWidget
from pymontecarlo_gui.widgets.util import create_group_box

# Globals and constants variables.

class ResultPlotWidget(QtWidgets.QWidget): #TODO implement Matplotlib

    def __init__(self, project=None):
        super().__init__()

        # Variables
        self._project = project
        self._result_class = None
        self._xray_lines = []
        self._selected_option = None

        self._xaxis = []
        self._yaxis = []

        self._update_xaxis()
        self._update_yaxis()

        # Widgets
        self.figure = figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def _update_xaxis(self):
        self._xaxis.clear()

        if self._project is None \
                or self._selected_option is None:
            return

        datarows = \
            self._project.create_options_datarows(True)

        if not datarows:
            return

        self._xaxis = \
            [datarow.to_list([self._selected_option]) for datarow in datarows]


    def _update_yaxis(self):
        self._yaxis.clear()

        if self._project is None \
                or self._result_class is None \
                or self._xray_lines == []:
            return

        datarows = \
            self._project.create_results_datarows([self._result_class])

        if not datarows:
            return

        self._yaxis = \
            [dict(datarow.to_list(self._xray_lines)) for datarow in datarows]

    def _plot(self):
        if self._xaxis == [] or self._yaxis == []:
            return
        # TODO plotting the axis with matplotlib

    def xaxis(self):
        return self._xaxis

    def yaxis(self):
        return self._yaxis

    def project(self):
        return self._project


    def setProject(self, project):
        self._project = project
        self._result_class = None
        self._xray_lines = []
        self._selected_option = None
        self._plot()


    def resultClass(self):
        return self._result_class


    def setResultClass(self, result_class):
        self._result_class = result_class
        self._xray_lines = []
        self._plot()


    def xrayLines(self):
        return self._xray_lines


    def setXrayLines(self, xray_lines):
        self._xray_lines = xray_lines
        self._update_yaxis()
        self._plot()


    def selectedOption(self):
        return self._selected_option


    def setSelectedOption(self, option):
        self._selected_option = option
        self._update_xaxis()
        self._plot()


class XrayLineListWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None, project=None):
        super().__init__(parent)

        # Variables
        self._project = project

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

    def setResultClass(self, resultclass=None):
        self.wdg_list.clear()
        if resultclass != None:
            datarow = self._project.create_results_datarows([resultclass])
            datarow_union = functools.reduce(operator.or_, datarow)
            lines = datarow_union.columns
            for line in lines:
                item = QtWidgets.QListWidgetItem(line)
                item.setData(QtCore.Qt.UserRole, None)
                item.setTextAlignment(QtCore.Qt.AlignLeft)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.wdg_list.addItem(item)

        self._update_toolbar()

    def xrayLines(self):
        lines = []

        for index in range(self.wdg_list.count()):
            item = self.wdg_list.item(index)
            if item.checkState() != QtCore.Qt.Checked:
                continue
            lines.append(item.data(QtCore.Qt.UserRole))

        return lines

    def setProject(self, project):
        self._project = project
        self.setResultClass(None)


class XaxisComboBoxWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.cmbbx_xaxis = QtWidgets.QComboBox()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.cmbbx_xaxis)
        self.setLayout(layout)

        # Signals
        self.cmbbx_xaxis.currentIndexChanged.connect(self._on_index_changed)

    def _on_index_changed(self, item):
        self.selectionChanged.emit()

    def setProject(self, project):
        self.cmbbx_xaxis.clear()
        self.cmbbx_xaxis.addItem('--- choose option ---', None)

        datarow_options = project.create_options_datarows(True)
        datarow_union = functools.reduce(operator.or_, datarow_options)
        options = datarow_union.columns

        for option in options:
            self.cmbbx_xaxis.addItem(option, option)

    def currentOption(self):
        option = self.cmbbx_xaxis.currentData()
        return option


class YaxisComboBoxWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.cmbbx_yaxis = QtWidgets.QComboBox()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.cmbbx_yaxis)
        self.setLayout(layout)

        # Signals
        self.cmbbx_yaxis.currentIndexChanged.connect(self._on_index_changed)

    def _on_index_changed(self, item):
        self.selectionChanged.emit()

    def setProject(self, project):
        classes = project.result_classes
        self.setResultClasses(classes)

    def currentResultClass(self):
        clasz = self.cmbbx_yaxis.currentData()
        return clasz

    def setResultClasses(self, classes):
        self.cmbbx_yaxis.clear()
        self.cmbbx_yaxis.addItem('--- choose result ---', None)

        for clasz in classes:
            name = clasz.getname()
            self.cmbbx_yaxis.addItem(name, clasz)


class ResultSummaryTableWidget(ResultSummaryWidget):

    COLUMN_WIDTH = 125

    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets
        self.plot = ResultPlotWidget()

        self.cmbbx_xaxis = XaxisComboBoxWidget()
        self.cmbbx_yaxis = YaxisComboBoxWidget()

        self.lst_xray_line = XrayLineListWidget()

        # Layouts
        lyt_right = QtWidgets.QVBoxLayout()
        lyt_right.addWidget(create_group_box('x-axis', self.cmbbx_xaxis))
        lyt_right.addWidget(create_group_box('y-axis', self.cmbbx_yaxis))
        lyt_right.addWidget(create_group_box('X-ray line', self.lst_xray_line))

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.plot, 3)
        layout.addLayout(lyt_right, 1)
        self.setLayout(layout)

        # Signals
        self.cmbbx_xaxis.selectionChanged.connect(self._on_xaxis_changed)
        self.cmbbx_yaxis.selectionChanged.connect(self._on_yaxis_changed)

        self.lst_xray_line.selectionChanged.connect(self._on_xray_line_changed)

    def _on_xaxis_changed(self):
        option = self.cmbbx_xaxis.currentOption()
        self.plot.setSelectedOption(option)

    def _on_yaxis_changed(self):
        clasz = self.cmbbx_yaxis.currentResultClass()
        self.lst_xray_line.setResultClass(clasz)
        self.plot.setResultClass(clasz)

    def _on_xray_line_changed(self):
        lines = self.lst_xray_line.xrayLines()
        self.plot.setXrayLines(lines)

    def setProject(self, project):
        self.cmbbx_xaxis.setProject(project)
        self.cmbbx_yaxis.setProject(project)
        self.lst_xray_line.setProject(project)
        self.plot.setProject(project)


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    from pymontecarlo.testcase import TestCase
    TestCase.setUpClass()
    testcase = TestCase()
    testcase.setUp()
    project = testcase.create_basic_project()

    #from pymontecarlo.project import Project
    #project = Project.read(filepath)

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
