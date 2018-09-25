from typing import List

from PyQt5 import QtCore
from PyQt5.QtWidgets import QCheckBox, QHeaderView, QMainWindow, QSplitter, \
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ui.galacticplot import GalacticPlot
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtgalacticplot import QtGalacticPlot


class QtMainWindow(MainWindow):

    def __init__(self):
        self.__window: QMainWindow = QMainWindow()
        self.__widget: QWidget = QSplitter(self.__window)
        self.__window.setCentralWidget(self.__widget)

        self.__planetListWidget: QTableWidget = QTableWidget()
        self.__planetListWidget.setColumnCount(1)
        self.__planetListWidget.setHorizontalHeaderLabels(["Planets"])
        self.__planetListWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.__tradeRouteListWidget: QTableWidget = QTableWidget()
        self.__tradeRouteListWidget.setColumnCount(1)
        self.__tradeRouteListWidget.setHorizontalHeaderLabels(["TradeRoutes"])
        self.__tradeRouteListWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        leftWidget: QWidget = QWidget()
        leftWidget.setLayout(QVBoxLayout())
        self.__widget.addWidget(leftWidget)

        leftWidget.layout().addWidget(self.__planetListWidget)
        leftWidget.layout().addWidget(self.__tradeRouteListWidget)

        self.__presenter: MainWindowPresenter = None

    def setMainWindowPresenter(self, presenter: MainWindowPresenter) -> None:
        self.__presenter = presenter

    def addPlanets(self, planets: List[str]) -> None:
        for planet in planets:
            rowCount = self.__planetListWidget.rowCount()
            self.__planetListWidget.setRowCount(rowCount + 1)
            item: QTableWidgetItem = QTableWidgetItem(planet)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.__planetListWidget.setItem(rowCount, 0, item)
        
        self.__planetListWidget.itemClicked.connect(self.__onPlanetTableWidgetItemClicked)

    def addTradeRoutes(self, tradeRoutes: List[str]) -> None:
        for tradeRoute in tradeRoutes:
            rowCount = self.__tradeRouteListWidget.rowCount()
            self.__tradeRouteListWidget.setRowCount(rowCount + 1)
            self.__tradeRouteListWidget.setCellWidget(rowCount, 0, QCheckBox())
            self.__tradeRouteListWidget.setItem(self.__tradeRouteListWidget.rowCount(), 0, QTableWidgetItem(tradeRoute))

    def makeGalacticPlot(self) -> GalacticPlot:
        plot: QtGalacticPlot = QtGalacticPlot(self.__widget)
        self.__widget.addWidget(plot.getWidget())
        return plot

    def getWindow(self) -> QMainWindow:
        return self.__window

    def __onPlanetTableWidgetItemClicked(self, item: QTableWidgetItem):
        checked: bool = False
        if item.checkState() == QtCore.Qt.Checked:
            checked = True

        self.__presenter.onPlanetChecked(item.row(), checked)
