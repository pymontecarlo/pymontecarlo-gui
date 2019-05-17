""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo.util.token import TokenState
from pymontecarlo_gui.widgets.color import check_color

# Globals and constants variables.

class TokenModel(QtCore.QAbstractTableModel):

    def __init__(self, token):
        super().__init__()
        self.token = token

    def rowCount(self, parent=None):
        return len(self.token.get_subtokens())

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        subtoken = self.token.get_subtokens()[row]

        if role == QtCore.Qt.UserRole:
            return subtoken

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return None

    def flags(self, index):
        return super().flags(index)

class TokenItemDelegate(QtWidgets.QItemDelegate):

    def _create_progressbar_option(self, token, option):
        progressbaroption = QtWidgets.QStyleOptionProgressBar()
        progressbaroption.state = QtWidgets.QStyle.State_Enabled
        progressbaroption.direction = QtCore.Qt.LeftToRight
        progressbaroption.rect = option.rect
        progressbaroption.fontMetrics = QtWidgets.QApplication.fontMetrics()
        progressbaroption.minimum = 0
        progressbaroption.maximum = 100
        progressbaroption.textAlignment = QtCore.Qt.AlignCenter
        progressbaroption.textVisible = True
        progressbaroption.progress = int(token.progress * 100)
        progressbaroption.text = token.status

        state = token.state
        color_highlight = QtGui.QColor(QtCore.Qt.red)
        if state == TokenState.RUNNING:
            color_highlight = QtGui.QColor(QtCore.Qt.green)
        elif state == TokenState.CANCELLED:
            color_highlight = check_color("#ff9600") # orange
        elif state == TokenState.ERROR:
            color_highlight = QtGui.QColor(QtCore.Qt.red)
        elif state == TokenState.DONE:
            color_highlight = QtGui.QColor(QtCore.Qt.blue)
        elif color_highlight == TokenState.NOTSTARTED:
            color_highlight = QtGui.QColor(QtCore.Qt.black)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Highlight, color_highlight)
        progressbaroption.palette = palette

        return progressbaroption

    def paint(self, painter, option, index):
        column = index.column()
        token = index.data(QtCore.Qt.UserRole)
        style = QtWidgets.QApplication.style()

        if column == 0:
            progressbaroption = self._create_progressbar_option(token, option)
            style.drawControl(QtWidgets.QStyle.CE_ProgressBar, progressbaroption, painter)

        else:
            super().paint(painter, option, index)

class TokenTableWidget(QtWidgets.QWidget):

    def __init__(self, token, parent=None):
        super().__init__(parent)

        # Variables
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.setSingleShot(False)

        # Widgets
        self.tableview = QtWidgets.QTableView()
        self.tableview.setModel(TokenModel(token))
        self.tableview.setItemDelegate(TokenItemDelegate())

        header = self.tableview.horizontalHeader()
        header.close()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setDefaultSectionSize(20)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tableview)
        self.setLayout(layout)

        # Signals
        self.timer.timeout.connect(self._on_timer_timeout)

        # Defaults
        self.timer.start()

    def _on_timer_timeout(self):
        model = self.tableview.model()
        model.modelReset.emit()

    def _on_tablewview_double_clicked(self, index):
        model = self.tableview.model()
        future = model.future(index.row())
        self.doubleClicked.emit(future)

