""""""

# Standard library modules.
import os

# Third party modules.
from qtpy import QtCore, QtWidgets

# Local modules.
import pymontecarlo_gui.widgets.messagebox as messagebox

# Globals and constants variables.

class _BrowseWidget(QtWidgets.QWidget):

    pathChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self._basedir = None

        # Widgets
        self._txt_path = QtWidgets.QLineEdit()
        self._txt_path.setReadOnly(True)

        btn_browse = QtWidgets.QPushButton("Browse")

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._txt_path, 1)
        layout.addWidget(btn_browse)
        self.setLayout(layout)

        # Signal
        btn_browse.released.connect(self._onBrowse)

    def _showDialog(self, basedir):
        raise NotImplementedError

    def _validatePath(self, path):
        raise NotImplementedError

    def _onBrowse(self):
        oldpath = self.path()
        newpath = self._showDialog(self.baseDir())

        if not newpath and not oldpath:
            return
        elif not newpath and oldpath:
            newpath = oldpath
        else:
            self.pathChanged.emit(newpath)

        try:
            self.setPath(newpath)
        except Exception as ex:
            messagebox.exception(self, ex)

    def setBaseDir(self, path):
        if not path:
            path = os.getcwd()

        if os.path.isfile(path):
            path = os.path.dirname(path)

        if not os.path.isdir(path):
            raise ValueError('%s is not a directory' % path)

        self._basedir = path

    def baseDir(self):
        return self._basedir or os.getcwd()

    def setPath(self, path, update_basedir=True):
        if not path:
            self._txt_path.setText('')
            self.pathChanged.emit(None)
            return

        path = os.path.abspath(path)

        self._validatePath(path)

        self._txt_path.setText(path)
        self._txt_path.setCursorPosition(0)

        if update_basedir:
            self.setBaseDir(path)
            os.chdir(self.baseDir())

        self.pathChanged.emit(path)

    def path(self):
        """
        Returns the path to the selected file.
        If no file is selected, the method returns ``None``
        """
        path = self._txt_path.text()
        return path if path else None

class FileBrowseWidget(_BrowseWidget):

    def __init__(self, parent=None):
        _BrowseWidget.__init__(self, parent=parent)

        # Variables
        self._namefilters = []

    def _showDialog(self, basedir):
        title = "Browse file"
        filter = ';;'.join(self.nameFilters())
        return QtWidgets.QFileDialog.getOpenFileName(self, title, basedir, filter)[0]

    def _validatePath(self, path):
        if os.path.splitext(path)[1] != '.app' and not os.path.isfile(path):
            raise ValueError('%s is not a file' % path)

    def setNameFilter(self, filter):
        self._namefilters.clear()
        self._namefilters.append(filter)

    def setNameFilters(self, filters):
        self._namefilters.clear()
        self._namefilters.extend(filters)

    def nameFilters(self):
        return list(self._namefilters)

class DirectoryBrowseWidget(_BrowseWidget):

    def _showDialog(self, basedir):
        title = "Browse directory"
        return QtWidgets.QFileDialog.getExistingDirectory(self, title, basedir)

    def _validatePath(self, path):
        if not os.path.isdir(path):
            raise ValueError('%s is not a directory' % path)
