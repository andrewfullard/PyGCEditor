from typing import List

from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction, QCheckBox, QFileDialog, QHeaderView, QMainWindow, QMenu, QMenuBar, QSplitter, \
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ui.galacticplot import GalacticPlot
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtgalacticplot import QtGalacticPlot


class QtMainWindow(MainWindow):

    def __init__(self):
        self.__window: QMainWindow = QMainWindow()
        self.__widget: QWidget = QSplitter(self.__window)
        self.__window.setCentralWidget(self.__widget)
        self.__window.setWindowTitle("Galactic Conquest Editor")

        self.__planetListWidget: QTableWidget = QTableWidget()
        self.__planetListWidget.setColumnCount(1)
        self.__planetListWidget.setHorizontalHeaderLabels(["Planets"])
        self.__planetListWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.__tradeRouteListWidget: QTableWidget = QTableWidget()
        self.__tradeRouteListWidget.setColumnCount(1)
        self.__tradeRouteListWidget.setHorizontalHeaderLabels(["TradeRoutes"])
        self.__tradeRouteListWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        #set up menu and menu options
        self.__menuBar: QMenuBar = QMenuBar()
        self.__menu: QMenu = QMenu("File", self.__window)
        
        self.__openAction: QAction = QAction("Open Galactic Conquest", self.__window)
        # self.__openAction.setStatusTip("Open a Galactic Conquest XML") #if we want a status bar
        self.__openAction.triggered.connect(self.__openFile)

        self.__saveAction: QAction = QAction("Save", self.__window)
        self.__saveAction.triggered.connect(self.__saveFile)

        self.__quitAction: QAction = QAction("Quit", self.__window)
        self.__quitAction.triggered.connect(self.__quit)
        
        self.__menu.addAction(self.__openAction)
        self.__menu.addAction(self.__saveAction)
        self.__menu.addAction(self.__quitAction)
        self.__menuBar.addMenu(self.__menu)
        self.__widget.addWidget(self.__menuBar)

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

    def __openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self.__widget,"Open Galactic Conquest", "","XML Files (*.xml);;All Files (*)")
        if fileName:
            print(fileName)

    def __saveFile(self):    
        fileName, _ = QFileDialog.getSaveFileName(self.__widget,"Save Galactic Conquest","","XML Files (*.xml);;All Files (*)")
        if fileName:
            print(fileName)

    def __quit(self):
        self.__window.close()
