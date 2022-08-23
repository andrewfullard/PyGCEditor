from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem

from ui.qttablewidgetfactory import QtTableWidgetFactory

class QtFactionsTable(QWidget):
    def __init__(self, parent: QWidget = None):
        super(QtFactionsTable, self).__init__()
        self.widget: QWidget = QWidget()
        self.widget.setLayout(QVBoxLayout())

        self.__tableWidgetFactory = QtTableWidgetFactory()

        self.factionListWidget = self.__tableWidgetFactory.construct(
            ["Factions", "Playable?", "AI control", "Story name"], columns=4
        )

        self.widget.layout().addWidget(self.factionListWidget)

    def empty(self) -> None:
        self.factionListWidget.clearContents()
        self.factionListWidget.setRowCount(0)

    def fillColumn(self, entries, column_index, checkbox=False) -> None:
        for row, entry in enumerate(entries):
            rowCount = self.factionListWidget.rowCount()

            if rowCount < len(entries):
                self.factionListWidget.setRowCount(rowCount + 1)

            item: QTableWidgetItem = QTableWidgetItem(entry)

            if checkbox:
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled)

            self.factionListWidget.setItem(row, column_index, item)