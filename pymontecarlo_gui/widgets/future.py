""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo_gui.widgets.color import check_color

# Globals and constants variables.

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

    def futures(self):
        return tuple(self._futures)

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
        act_clear = toolbar.addAction(QtGui.QIcon.fromTheme('edit-clear'), "Clear done future")

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tableview)
        layout.addWidget(toolbar)
        self.setLayout(layout)

        # Signals
        self.timer.timeout.connect(self._on_timer_timeout)

        act_clear.triggered.connect(self._on_clear)

    def _on_timer_timeout(self):
        model = self.tableview.model()

        if all(not future.running() for future in model.futures()):
            self.timer.stop()

        model.modelReset.emit()

    def _on_clear(self):
        model = self.tableview.model()
        model.clearDoneFutures()

    def addFuture(self, future):
        model = self.tableview.model()
        model.addFuture(future)
        self.timer.start()



