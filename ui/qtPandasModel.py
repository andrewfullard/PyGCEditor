from PyQt6.QtCore import QAbstractTableModel, Qt


class PandasModel(QAbstractTableModel):
    def __init__(self, data, filter):
        super().__init__()
        self._data = data
        self._filter = filter
        self._filter_column = "Planet"
        self._mask = self._data[self._filter_column] == self._filter

    def rowCount(self, index):
        if self._filter:
            return self._data.loc[self._mask].shape[0]
        else:
            return self._data.shape[0]

    def columnCount(self, parent=None):
        if self._filter:
            return self._data.loc[self._mask].shape[1]
        else:
            return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                if self._filter:
                    # Attempt to filter the view in-place
                    value = self._data.loc[self._mask].iat[index.row(), index.column()]
                else:
                    value = self._data.iloc[index.row(), index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            if self._filter:
                start_index = self._data.loc[self._mask].index[0]
                self._data.iloc[index.row() + start_index, index.column()] = value
            else:
                self._data.loc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def sort(self, column, order):
        colname = self._data.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._data.sort_values(
            colname, ascending=order == Qt.SortOrder.AscendingOrder, inplace=True
        )
        self._data.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()
