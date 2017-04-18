""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo.util.future import FutureAdapter

from pymontecarlo_gui.widgets.color import check_color

# Globals and constants variables.

class ExecutorCancelThread(QtCore.QThread):

    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    def run(self):
        self.executor.cancel()

class FutureThread(QtCore.QThread):

    progressChanged = QtCore.Signal(int)
    statusChanged = QtCore.Signal(str)

    def __init__(self, future):
        super().__init__()
        self.future = future

    def run(self):
        while self.future.running():
            self.progressChanged.emit(int(self.future.progress * 100))
            self.statusChanged.emit(self.future.status)
            self.sleep(1)

        self.progressChanged.emit(int(self.future.progress * 100))
        self.statusChanged.emit(self.future.status)

class FutureModel(QtCore.QAbstractTableModel):

    def __init__(self):
        super().__init__()
        self._futures = []

    def rowCount(self, parent=None):
        return len(self._futures)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        future = self._futures[row]

        if role == QtCore.Qt.UserRole:
            return future

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return None

    def flags(self, index):
        return super().flags(index)

    def addFuture(self, future):
        self._futures.append(future)
        self.modelReset.emit()

    def clearDoneFutures(self):
        for i in reversed(range(len(self._futures))):
            if self._futures[i].done():
                self._futures.pop(i)
        self.modelReset.emit()

    def hasDoneFutures(self):
        return any(future.done() for future in self._futures)

    def futures(self):
        return tuple(self._futures)

    def future(self, row):
        return self._futures[row]

class FutureItemDelegate(QtWidgets.QItemDelegate):

    def _create_progressbar_option(self, future, option):
        progressbaroption = QtWidgets.QStyleOptionProgressBar()
        progressbaroption.state = QtWidgets.QStyle.State_Enabled
        progressbaroption.direction = QtCore.Qt.LeftToRight
        progressbaroption.rect = option.rect
        progressbaroption.fontMetrics = QtWidgets.QApplication.fontMetrics()
        progressbaroption.minimum = 0
        progressbaroption.maximum = 100
        progressbaroption.textAlignment = QtCore.Qt.AlignCenter
        progressbaroption.textVisible = True
        progressbaroption.progress = int(future.progress * 100)
        progressbaroption.text = future.status

        try:
            if future.running():
                color_highlight = QtGui.QColor(QtCore.Qt.green)
            elif future.cancelled():
                color_highlight = check_color("#ff9600") # orange
            elif future.done():
                if future.exception():
                    color_highlight = QtGui.QColor(QtCore.Qt.red)
                else:
                    color_highlight = QtGui.QColor(QtCore.Qt.blue)
            else:
                color_highlight = QtGui.QColor(QtCore.Qt.black)
        except:
            color_highlight = QtGui.QColor(QtCore.Qt.red)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Highlight, color_highlight)
        progressbaroption.palette = palette

        return progressbaroption

    def _create_button_option(self, future, option):
        buttonoption = QtWidgets.QStyleOptionButton()

        if future.cancelled() or future.done():
            state = QtWidgets.QStyle.State_None
        else:
            state = QtWidgets.QStyle.State_Enabled

        buttonoption.state = state
        buttonoption.direction = QtCore.Qt.LeftToRight
        buttonoption.rect = option.rect
        buttonoption.fontMetrics = QtWidgets.QApplication.fontMetrics()
        buttonoption.icon = QtGui.QIcon.fromTheme('edit-delete')
        buttonoption.iconSize = QtCore.QSize(16, 16)
        return buttonoption

    def paint(self, painter, option, index):
        column = index.column()
        future = index.data(QtCore.Qt.UserRole)
        style = QtWidgets.QApplication.style()

        if column == 0:
            progressbaroption = self._create_progressbar_option(future, option)
            style.drawControl(QtWidgets.QStyle.CE_ProgressBar, progressbaroption, painter)

        elif column == 1:
            buttonoption = self._create_button_option(future, option)
            style.drawControl(QtWidgets.QStyle.CE_PushButton, buttonoption, painter)

        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if index.column() != 1:
            return super().editorEvent(event, model, option, index)

        if event.type() != QtCore.QEvent.MouseButtonRelease:
            return super().editorEvent(event, model, option, index)

        if not option.rect.contains(event.pos()):
            return super().editorEvent(event, model, option, index)

        future = index.data(QtCore.Qt.UserRole)
        if future.cancelled() or future.done():
            return super().editorEvent(event, model, option, index)

        future.cancel()

        return super().editorEvent(event, model, option, index)

class FutureTableWidget(QtWidgets.QWidget):

    doubleClicked = QtCore.Signal(FutureAdapter)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.setSingleShot(False)

        # Widgets
        self.tableview = QtWidgets.QTableView()
        self.tableview.setModel(FutureModel())
        self.tableview.setItemDelegate(FutureItemDelegate())

        header = self.tableview.horizontalHeader()
        header.close()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setDefaultSectionSize(20)

        toolbar = QtWidgets.QToolBar()
        self.act_clear = toolbar.addAction("Clear done future(s)")
        self.act_clear.setIcon(QtGui.QIcon.fromTheme('edit-clear'))
        self.act_clear.setEnabled(False)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tableview)
        layout.addWidget(toolbar, alignment=QtCore.Qt.AlignRight)
        self.setLayout(layout)

        # Signals
        self.timer.timeout.connect(self._on_timer_timeout)

        self.tableview.model().modelReset.connect(self._on_model_reset)
        self.tableview.doubleClicked.connect(self._on_tablewview_double_clicked)

        self.act_clear.triggered.connect(self._on_clear)

    def _on_timer_timeout(self):
        model = self.tableview.model()

        if all(not future.running() for future in model.futures()):
            self.timer.stop()

        model.modelReset.emit()

    def _on_model_reset(self):
        model = self.tableview.model()
        has_done_futures = model.hasDoneFutures()
        self.act_clear.setEnabled(has_done_futures)

    def _on_tablewview_double_clicked(self, index):
        model = self.tableview.model()
        future = model.future(index.row())
        self.doubleClicked.emit(future)

    def _on_clear(self):
        model = self.tableview.model()
        model.clearDoneFutures()

    def addFuture(self, future):
        model = self.tableview.model()
        model.addFuture(future)
        self.timer.start()

