""""""

# Standard library modules.

# Third party modules.
from qtpy import QtCore, QtGui, QtWidgets

# Local modules.
from pymontecarlo.settings import XrayNotation

# Globals and constants variables.

class PhotonSingleResultModel(QtCore.QAbstractTableModel):

    def __init__(self, result, settings, value_label, value_units=None):
        super().__init__()
        self.rows = self._extract_rows(result)
        self.settings = settings
        self.value_label = value_label
        self.value_units = value_units

    def _extract_rows(self, result):
        return list(result.items())

    def rowCount(self, parent=None):
        return len(self.rows)

    def columnCount(self, parent=None):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        irow = index.row()
        icolumn = index.column()

        xrayline, value = self.rows[irow]

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.UserRole, QtCore.Qt.EditRole]:
            if icolumn == 0:
                return xrayline.iupac if self.settings.preferred_xray_notation == XrayNotation.IUPAC else xrayline.siegbahn
            elif icolumn == 1:
                return '{:g}'.format(self.settings.to_preferred_unit(value.n, self.value_units).magnitude)
            elif icolumn == 2:
                return '{:g}'.format(self.settings.to_preferred_unit(value.s, self.value_units).magnitude)

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role not in [QtCore.Qt.DisplayRole, QtCore.Qt.UserRole]:
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return 'X-ray line'
            elif section == 1:
                if self.value_units:
                    return '{} [{}]'.format(self.value_label, self.value_units)
                else:
                    return self.value_label
            elif section == 2:
                if self.value_units:
                    return 'Uncertainty [{}]'.format(self.value_units)
                else:
                    return 'Uncertainty'

        elif orientation == QtCore.Qt.Vertical:
            return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(super().flags(index)) | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

