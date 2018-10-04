from typing import List

from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction, QPushButton, QCheckBox, QComboBox, QFileDialog, QHeaderView, QMainWindow, QMenu, QMenuBar, QSplitter, \
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ui.galacticplot import GalacticPlot
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtgalacticplot import QtGalacticPlot
from ui.qtcampaigncreator import QtCampaignCreator
from xml.xmlstructure import XMLStructure

class QtMainWindow(MainWindow):

    def __init__(self):
        self.__allPlanetsChecked: bool = False
        self.__allTradeRoutesChecked: bool = False

        self.__window: QMainWindow = QMainWindow()
        self.__widget: QWidget = QSplitter(self.__window)
        self.__window.setCentralWidget(self.__widget)
        self.__window.setWindowTitle("Galactic Conquest Editor")

        self.__campaignComboBox: QComboBox = QComboBox()

        self.__campaignCreator = QtCampaignCreator()

        self.__planetListWidget: QTableWidget = QTableWidget()
        self.__planetListWidget.setColumnCount(1)
        self.__planetListWidget.setHorizontalHeaderLabels(["Planets"])
        self.__planetListWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.__planetListWidget.verticalHeader().setVisible(False)

        self.__tradeRouteListWidget: QTableWidget = QTableWidget()
        self.__tradeRouteListWidget.setColumnCount(1)
        self.__tradeRouteListWidget.setHorizontalHeaderLabels(["Trade Routes"])
        self.__tradeRouteListWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.__tradeRouteListWidget.verticalHeader().setVisible(False)

        self.__selectAllPlanetsButton: QPushButton = QPushButton("Select All Planets")
        self.__selectAllPlanetsButton.clicked.connect(lambda: self.__selectAllPlanetsButtonClicked(self.__planetListWidget, True))

        self.__deselectAllPlanetsButton: QPushButton = QPushButton("Deselect All Planets")
        self.__deselectAllPlanetsButton.clicked.connect(lambda: self.__selectAllPlanetsButtonClicked(self.__planetListWidget, False))

        self.__selectAllTradeRoutesButton: QPushButton = QPushButton("Select All Trade Routes")
        self.__selectAllTradeRoutesButton.clicked.connect(lambda: self.__selectAllTradeRoutesButtonClicked(self.__tradeRouteListWidget, True))

        self.__deselectAllTradeRoutesButton: QPushButton = QPushButton("Deselect All Trade Routes")
        self.__deselectAllTradeRoutesButton.clicked.connect(lambda: self.__selectAllTradeRoutesButtonClicked(self.__tradeRouteListWidget, False))

        #set up menu and menu options
        self.__menuBar: QMenuBar = QMenuBar()
        self.__menu: QMenu = QMenu("File", self.__window)
        
        self.__newAction: QAction = QAction("New Galactic Conquest...", self.__window)
        self.__newAction.triggered.connect(self.__campaignCreator.showDialog)

        self.__openAction: QAction = QAction("Open Galactic Conquest", self.__window)
        # self.__openAction.setStatusTip("Open a Galactic Conquest XML") #if we want a status bar
        self.__openAction.triggered.connect(self.__openFile)

        self.__setDataFolderAction: QAction = QAction("Set Data Folder", self.__window)
        self.__setDataFolderAction.triggered.connect(self.__openFolder)

        self.__saveAction: QAction = QAction("Save", self.__window)
        self.__saveAction.triggered.connect(self.__saveFile)

        self.__quitAction: QAction = QAction("Quit", self.__window)
        self.__quitAction.triggered.connect(self.__quit)
        
        self.__menu.addAction(self.__newAction)
        self.__menu.addAction(self.__openAction)
        self.__menu.addAction(self.__saveAction)
        self.__menu.addAction(self.__setDataFolderAction)
        self.__menu.addAction(self.__quitAction)
        self.__menuBar.addMenu(self.__menu)
        self.__widget.addWidget(self.__menuBar)

        leftWidget: QWidget = QWidget()
        leftWidget.setLayout(QVBoxLayout())
        self.__widget.addWidget(leftWidget)

        leftWidget.layout().addWidget(self.__campaignComboBox)
        leftWidget.layout().addWidget(self.__planetListWidget)
        leftWidget.layout().addWidget(self.__selectAllPlanetsButton)
        leftWidget.layout().addWidget(self.__deselectAllPlanetsButton)
        leftWidget.layout().addWidget(self.__tradeRouteListWidget)
        leftWidget.layout().addWidget(self.__selectAllTradeRoutesButton)
        leftWidget.layout().addWidget(self.__deselectAllTradeRoutesButton)

        self.__presenter: MainWindowPresenter = None

    def setMainWindowPresenter(self, presenter: MainWindowPresenter) -> None:
        self.__presenter = presenter

    def addPlanets(self, planets: List[str]) -> None:
        self.__addEntriesToTableWidget(self.__planetListWidget, planets)
        self.__planetListWidget.itemClicked.connect(self.__onPlanetTableWidgetItemClicked)

    def addTradeRoutes(self, tradeRoutes: List[str]) -> None:
        self.__addEntriesToTableWidget(self.__tradeRouteListWidget, tradeRoutes)
        self.__tradeRouteListWidget.itemClicked.connect(self.__onTradeRouteTableWidgetItemClicked)

    def addCampaigns(self, campaigns: List[str]) -> None:
        self.__campaignComboBox.addItems(campaigns)
        self.__campaignComboBox.activated.connect(self.__onCampaignSelected)

    def makeGalacticPlot(self) -> GalacticPlot:
        plot: QtGalacticPlot = QtGalacticPlot(self.__widget)
        self.__widget.addWidget(plot.getWidget())
        return plot

    def getWindow(self) -> QMainWindow:
        return self.__window

    def __addEntriesToTableWidget(self, widget: QTableWidget, entries: List[str]) -> None:
        for entry in entries:
            rowCount = widget.rowCount()
            widget.setRowCount(rowCount + 1)
            item: QTableWidgetItem = QTableWidgetItem(entry)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            widget.setItem(rowCount, 0, item)

    def __onPlanetTableWidgetItemClicked(self, item: QTableWidgetItem) -> None:
        checked: bool = False
        if item.checkState() == QtCore.Qt.Checked:
            checked = True

        self.__presenter.onPlanetChecked(item.row(), checked)

    def __onTradeRouteTableWidgetItemClicked(self, item: QTableWidgetItem) -> None:
        checked: bool = False
        if item.checkState() == QtCore.Qt.Checked:
            checked = True

        self.__presenter.onTradeRouteChecked(item.row(), checked)

    def __openFile(self) -> None:
        fileName, _ = QFileDialog.getOpenFileName(self.__widget,"Open Galactic Conquest", "","XML Files (*.xml);;All Files (*)")
        if fileName:
            print(fileName)

    def __openFolder(self) -> None:
        folderName = QFileDialog.getExistingDirectory(self.__widget, 'Select Data folder:', "", QFileDialog.ShowDirsOnly)
        if folderName:
            print(folderName)
            XMLStructure.dataFolder = folderName

    def __saveFile(self) -> None:    
        fileName, _ = QFileDialog.getSaveFileName(self.__widget,"Save Galactic Conquest","","XML Files (*.xml);;All Files (*)")
        if fileName:
            print(fileName)

    def __quit(self) -> None:
        self.__window.close()

    def __selectAllPlanetsButtonClicked(self, table: QTableWidget, checked: bool) -> None:
        rowCount = table.rowCount()

        if checked:
            for row in range(rowCount):
                item = table.item(row, 0)
                item.setCheckState(2)
            
            self.__presenter.allPlanetsChecked(True)
        
        else:
            for row in range(rowCount):
                item = table.item(row, 0)
                item.setCheckState(0)
            
            self.__presenter.allPlanetsChecked(False)
        
    
    def __selectAllTradeRoutesButtonClicked(self, table: QTableWidget, checked: bool) -> None:
        rowCount = table.rowCount()
        
        if checked:
            for row in range(rowCount):
                item = table.item(row, 0)
                item.setCheckState(2)
            
            self.__presenter.allTradeRoutesChecked(True)
        
        else:
            for row in range(rowCount):
                item = table.item(row, 0)
                item.setCheckState(0)
            
            self.__presenter.allTradeRoutesChecked(False)

    def __onCampaignSelected(self, index: int):
        self.__presenter.onCampaignSelected(index)
