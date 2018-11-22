from typing import List

from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction, QPushButton, QCheckBox, QComboBox, QFileDialog, QHeaderView, QLabel, QMainWindow, QMenu, QMenuBar, QDialog, QSplitter, \
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ui.galacticplot import GalacticPlot
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtgalacticplot import QtGalacticPlot
from ui.qtcampaignproperties import QtCampaignProperties
from ui.qttraderoutecreator import QtTradeRouteCreator
from ui.qttablewidgetfactory import QtTableWidgetFactory
from xml.xmlstructure import XMLStructure

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute

class QtMainWindow(MainWindow):
    '''Qt based window'''
    def __init__(self):
        self.__allPlanetsChecked: bool = False
        self.__allTradeRoutesChecked: bool = False

        self.__window: QMainWindow = QMainWindow()
        self.__widget: QWidget = QSplitter(self.__window)
        self.__window.setCentralWidget(self.__widget)
        self.__window.setWindowTitle("Galactic Conquest Editor")

        self.__campaignComboBox: QComboBox = QComboBox()
        self.__campaignPropertiesButton: QPushButton = QPushButton("Campaign Properties")
        self.__campaignPropertiesButton.clicked.connect(self.__campaignPropertiesButtonClicked)

        self.__campaignProperties = QtCampaignProperties()
        self.__tradeRouteCreator = QtTradeRouteCreator()

        self.__tableWidgetFactory = QtTableWidgetFactory()

        self.__planetListWidget = self.__tableWidgetFactory.construct("Planets")

        self.__tradeRouteListWidget = self.__tableWidgetFactory.construct("Trade Routes")

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
        self.__fileMenu: QMenu = QMenu("File", self.__window)
        self.__addMenu: QMenu = QMenu("New...", self.__window)
        
        self.__newCampaignAction: QAction = QAction("Galactic Conquest...", self.__window)
        self.__newCampaignAction.triggered.connect(self.__newCampaign)

        self.__newTradeRouteAction: QAction = QAction("Trade Route...", self.__window)
        self.__newTradeRouteAction.triggered.connect(self.__newTradeRoute)

        self.__setDataFolderAction: QAction = QAction("Set Data Folder", self.__window)
        self.__setDataFolderAction.triggered.connect(self.__openFolder)

        self.__saveAction: QAction = QAction("Save", self.__window)
        self.__saveAction.triggered.connect(self.__saveFile)

        self.__quitAction: QAction = QAction("Quit", self.__window)
        self.__quitAction.triggered.connect(self.__quit)
        
        self.__fileMenu.addAction(self.__saveAction)
        self.__fileMenu.addAction(self.__setDataFolderAction)
        self.__fileMenu.addAction(self.__quitAction)

        self.__addMenu.addAction(self.__newCampaignAction)
        self.__addMenu.addAction(self.__newTradeRouteAction)

        self.__menuBar.addMenu(self.__fileMenu)
        self.__menuBar.addMenu(self.__addMenu)
        self.__window.setMenuWidget(self.__menuBar)

        leftWidget: QWidget = QWidget()
        leftWidget.setLayout(QVBoxLayout())
        self.__widget.addWidget(leftWidget)

        leftWidget.layout().addWidget(self.__campaignComboBox)
        leftWidget.layout().addWidget(self.__campaignPropertiesButton)
        leftWidget.layout().addWidget(self.__planetListWidget)
        leftWidget.layout().addWidget(self.__selectAllPlanetsButton)
        leftWidget.layout().addWidget(self.__deselectAllPlanetsButton)
        leftWidget.layout().addWidget(self.__tradeRouteListWidget)
        leftWidget.layout().addWidget(self.__selectAllTradeRoutesButton)
        leftWidget.layout().addWidget(self.__deselectAllTradeRoutesButton)

        self.__presenter: MainWindowPresenter = None

    def setMainWindowPresenter(self, presenter: MainWindowPresenter) -> None:
        '''Set the presenter class for the window'''
        self.__presenter = presenter

    def addPlanets(self, planets: List[str]) -> None:
        '''Add Planet objects to the planet table widget'''
        self.__addEntriesToTableWidget(self.__planetListWidget, planets)
        self.__planetListWidget.itemClicked.connect(self.__onPlanetTableWidgetItemClicked)

    def addTradeRoutes(self, tradeRoutes: List[str]) -> None:
        '''Add TradeRoute objects to the trade route table widget'''
        self.__addEntriesToTableWidget(self.__tradeRouteListWidget, tradeRoutes)
        self.__tradeRouteListWidget.itemClicked.connect(self.__onTradeRouteTableWidgetItemClicked)

    def updateTradeRoutes(self, tradeRoutes: List[str]) -> None:
        '''Update TradeRoute trade route table widget'''
        self.__tradeRouteListWidget.clearContents()
        self.__tradeRouteListWidget.setRowCount(0)
        self.__addEntriesToTableWidget(self.__tradeRouteListWidget, tradeRoutes)
        self.__tradeRouteListWidget.itemClicked.connect(self.__onTradeRouteTableWidgetItemClicked)

    def addCampaigns(self, campaigns: List[str]) -> None:
        '''Add Campaign objects to the campaign combobox widget'''
        self.__campaignComboBox.addItems(campaigns)
        self.__campaignComboBox.activated.connect(self.__onCampaignSelected)

    def makeGalacticPlot(self) -> GalacticPlot:
        '''Plot planets and trade routes'''
        plot: QtGalacticPlot = QtGalacticPlot(self.__widget)
        self.__widget.addWidget(plot.getWidget())
        return plot

    def getWindow(self) -> QMainWindow:
        return self.__window

    def emptyWidgets(self) -> None:
        '''Clears all list and combobox widgets'''
        self.__planetListWidget.clearContents()
        self.__planetListWidget.setRowCount(0)
        self.__tradeRouteListWidget.clearContents()
        self.__tradeRouteListWidget.setRowCount(0)
        self.__campaignComboBox.clear()

    def updateCampaignComboBox(self, campaigns: List[str], newCampaign: str) -> None:
        '''Update the campaign combobox'''
        self.__campaignComboBox.clear()
        self.__campaignComboBox.addItems(campaigns)
        newCampaignIndex = self.__campaignComboBox.findText(newCampaign)
        self.__campaignComboBox.setCurrentIndex(newCampaignIndex)
        self.__onCampaignSelected(newCampaignIndex)
    
    def updatePlanetSelection(self, planets: List[int]) -> None:
        '''Clears table, then checks off planets in the table from a list of indexes'''
        self.__uncheckAllTable(self.__planetListWidget)

        for p in planets:
            self.__planetListWidget.item(p, 0).setCheckState(QtCore.Qt.Checked)
    
    def updateTradeRouteSelection(self, tradeRoutes: List[int]) -> None:
        '''Clears table, then checks off trade routes in the table from a list of indexes'''
        self.__uncheckAllTable(self.__tradeRouteListWidget)

        for t in tradeRoutes:
            print(self.__tradeRouteListWidget.item(t, 0), t)
            self.__tradeRouteListWidget.item(t, 0).setCheckState(QtCore.Qt.Checked)

    def displayLoadingScreen(self) -> QDialog:
        '''Displays a loading screen'''
        screen: QDialog = QDialog()
        layout = QVBoxLayout()
        label = QLabel("Loading Mod Data...")

        screen.setWindowTitle("Loading...")
        screen.setBaseSize(100, 100)
        layout.addWidget(label)

        screen.setWindowFlags(QtCore.Qt.WindowTitleHint)
        screen.setLayout(layout)

        return screen

    def clearPlanets(self) -> None:
        '''Helper function to clear planet selections from the presenter'''
        self.__uncheckAllTable(self.__planetListWidget)
    
    def clearTradeRoutes(self) -> None:
        '''Helper function to clear traderoute selections from the presenter'''
        self.__uncheckAllTable(self.__tradeRouteListWidget)

    def __addEntriesToTableWidget(self, widget: QTableWidget, entries: List[str]) -> None:
        '''Adds a list of rows to a table widget'''
        for entry in entries:
            rowCount = widget.rowCount()
            widget.setRowCount(rowCount + 1)
            item: QTableWidgetItem = QTableWidgetItem(entry)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            widget.setItem(rowCount, 0, item)

    def __onPlanetTableWidgetItemClicked(self, item: QTableWidgetItem) -> None:
        '''If a planet table widget item is clicked, check it and call the presenter to display it'''
        checked: bool = False
        if item.checkState() == QtCore.Qt.Checked:
            checked = True

        self.__presenter.onPlanetChecked(item.row(), checked)

    def __onTradeRouteTableWidgetItemClicked(self, item: QTableWidgetItem) -> None:
        '''If a trade route table widget item is clicked, check it and call the presenter to display it'''
        checked: bool = False
        if item.checkState() == QtCore.Qt.Checked:
            checked = True

        self.__presenter.onTradeRouteChecked(item.row(), checked)

    def __newCampaign(self) -> None:
        '''Helper function to launch the new campaign dialog with a presenter connection'''
        if self.__presenter is not None:
            self.__campaignProperties.showDialog(self.__presenter)

    def __openFolder(self) -> None:
        '''Set data folder dialog'''
        folderName = QFileDialog.getExistingDirectory(self.__widget, 'Select Data folder:', "", QFileDialog.ShowDirsOnly)
        if folderName:
            self.__presenter.onDataFolderChanged(folderName)

    def __newTradeRoute(self) -> None:
        '''Helper function to launch the new trade route dialog'''
        if self.__presenter is not None:
            self.__tradeRouteCreator.showDialog(self.__presenter)

    def __saveFile(self) -> None:    
        '''Save file dialog'''
        fileName, _ = QFileDialog.getSaveFileName(self.__widget,"Save Galactic Conquest","","XML Files (*.xml);;All Files (*)")
        if fileName:
            self.__presenter.saveFile(fileName)

    def __quit(self) -> None:
        '''Exits application by closing the window'''
        self.__window.close()

    def __selectAllPlanetsButtonClicked(self, table: QTableWidget, checked: bool) -> None:
        '''Cycles through a table and checks all the planet entries, then presents them'''
        rowCount = table.rowCount()

        if checked:
            self.__checkAllTable(table)
            
            self.__presenter.allPlanetsChecked(True)
        
        else:
            self.__uncheckAllTable(table)
            
            self.__presenter.allPlanetsChecked(False)
        
    
    def __selectAllTradeRoutesButtonClicked(self, table: QTableWidget, checked: bool) -> None:
        '''Cycles through a table and checks all the trade route entries, then presents them'''        
        if checked:
            self.__checkAllTable(table)
            
            self.__presenter.allTradeRoutesChecked(True)
        
        else:
            self.__uncheckAllTable(table)
            
            self.__presenter.allTradeRoutesChecked(False)

    def __onCampaignSelected(self, index: int) -> None:
        '''Presents a selected campaign'''
        self.__presenter.onCampaignSelected(index)

    def __checkAllTable(self, table: QTableWidget) -> None:
        rowCount = table.rowCount()
        for row in range(rowCount):
            table.item(row, 0).setCheckState(QtCore.Qt.Checked)

    def __uncheckAllTable(self, table: QTableWidget) -> None:
        rowCount = table.rowCount()
        for row in range(rowCount):
            table.item(row, 0).setCheckState(QtCore.Qt.Unchecked)

    def __campaignPropertiesButtonClicked(self) -> None:
        campaign = self.__campaignComboBox.currentIndex()
        self.__campaignProperties.showDialog(self.__presenter, campaign)
