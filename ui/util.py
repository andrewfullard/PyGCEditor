from typing import List

from PyQt6 import QtCore
from PyQt6.QtWidgets import QTableWidget

def checkAllTable(table: QTableWidget) -> None:
    """Checks all rows in a table widget"""
    rowCount = table.rowCount()
    for row in range(rowCount):
        table.item(row, 0).setCheckState(QtCore.Qt.CheckState.Checked)

def uncheckAllTable(table: QTableWidget) -> None:
    """Unchecks all rows in a table widget"""
    rowCount = table.rowCount()
    for row in range(rowCount):
        table.item(row, 0).setCheckState(QtCore.Qt.CheckState.Unchecked)

def checkListTable(table: QTableWidget, list: List) -> None:
    """Checks specific rows in a table widget"""
    uncheckAllTable(table)

    for index in list:
        table.item(index, 0).setCheckState(QtCore.Qt.CheckState.Checked)