from typing import List
import pandas as pd

from PyQt6 import QtCore
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QPushButton,
    QComboBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSplitter,
    QTableWidget,
    QTableView,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.galacticplot import GalacticPlot
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtgalacticplot import QtGalacticPlot
from ui.qtPandasModel import PandasModel
from ui.qttablewidgetfactory import QtTableWidgetFactory
from ui.qtplanetstraderoutes import QtPlanetsTradeRoutes
from ui.util import checkAllTable, uncheckAllTable, checkListTable

from gameObjects.planet import Planet


class QtMainWindow(MainWindow):
    """Qt based window"""

    def __init__(self):
        # Main window setup
        self.__window: QMainWindow = QMainWindow()
        self.__widget: QWidget = QSplitter(self.__window)
        self.__window.setCentralWidget(self.__widget)
        self.__window.setWindowTitle("Galactic Conquest Editor")

        self.__importStartingForcesButton: QPushButton = QPushButton(
            "Import Default Forces"
        )
        self.__importStartingForcesButton.clicked.connect(
            self.__importStartingForcesButtonClicked
        )

        self.__tableWidgetFactory = QtTableWidgetFactory()

        self.__factionListWidget = self.__tableWidgetFactory.construct(
            ["Playable Factions"]
        )

        # Left pane, Forces tab
        self.__planetComboBox: QComboBox = QComboBox()

        self.__openAutoConnectionSettingsAction: QAction = QAction(
            "Auto connection settings", self.__window
        )
        self.__openAutoConnectionSettingsAction.triggered.connect(
            self.__showAutoConnectionSettings
        )
        self.__forcesListTable = QTableView()
        self.__forcesListTable.setSortingEnabled(False)

        self.__planetInfoLabel: QLabel = QLabel()
        self.__totalPlanetForceLabel: QLabel = QLabel()
        self.__totalPlanetForceLabel.setText("Total force at planet: ")
        self.__totalFactionForceLabel: QLabel = QLabel()
        self.__totalFactionForceLabel.setText(
            "Select a campaign to see total starting forces per faction"
        )

        # set up menu and menu options
        self.__menuBar: QMenuBar = QMenuBar()
        self.__fileMenu: QMenu = QMenu("File", self.__window)
        self.__optionsMenu: QMenu = QMenu("Options", self.__window)
        self.__addMenu: QMenu = QMenu("New...", self.__window)

        self.__newCampaignAction: QAction = QAction(
            "Galactic Conquest...", self.__window
        )
        self.__newCampaignAction.triggered.connect(self.__newCampaign)

        self.__newTradeRouteAction: QAction = QAction("Trade Route...", self.__window)
        self.__newTradeRouteAction.triggered.connect(self.__newTradeRoute)

        self.__setDataFolderAction: QAction = QAction("Set Data Folder", self.__window)
        self.__setDataFolderAction.triggered.connect(self.__openFolder)

        self.__saveAction: QAction = QAction("Save", self.__window)
        self.__saveAction.triggered.connect(self.__saveFile)

        self.__importForcesSaveAction: QAction = QAction("Import Default Forces and Save", self.__window)
        self.__importForcesSaveAction.triggered.connect(self.__importForcesSaveFile)

        self.__quitAction: QAction = QAction("Quit", self.__window)
        self.__quitAction.triggered.connect(self.__quit)

        self.__optionsMenu.addAction(self.__openAutoConnectionSettingsAction)

        self.__fileMenu.addAction(self.__saveAction)
        self.__fileMenu.addAction(self.__importForcesSaveAction)
        self.__fileMenu.addAction(self.__setDataFolderAction)
        self.__fileMenu.addAction(self.__quitAction)

        self.__addMenu.addAction(self.__newCampaignAction)
        self.__addMenu.addAction(self.__newTradeRouteAction)

        self.__menuBar.addMenu(self.__fileMenu)
        self.__menuBar.addMenu(self.__addMenu)
        self.__menuBar.addMenu(self.__optionsMenu)
        self.__window.setMenuWidget(self.__menuBar)

        # Set up left pane tabs
        self.__leftTabsWidget: QWidget = QTabWidget()
        self.__GCLayoutWidget = QtPlanetsTradeRoutes()
        self.__startingForces: QWidget = QWidget()
        self.__factions: QWidget = QWidget()
        
        # Left pane, GC layout tab
        self.__GCLayoutWidget.campaignComboBoxSignal.connect(self.__onCampaignSelected)
        self.__GCLayoutWidget.campaignPropertiesButtonSignal.connect(self.__campaignPropertiesButtonClicked)
        self.__GCLayoutWidget.planetListWidgetContextSignal.connect(self.__showPlanetContextMenu)
        self.__GCLayoutWidget.planetListWidgetSignal.connect(self.__onPlanetTableWidgetItemClicked)
        self.__GCLayoutWidget.tradeRouteListWidgetSignal.connect(self.__onTradeRouteTableWidgetItemClicked)

        self.__leftTabsWidget.addTab(self.__GCLayoutWidget.widget, "Layout")
        self.__leftTabsWidget.addTab(self.__startingForces, "Forces")

        self.__leftTabsWidget.addTab(self.__factions, "Factions")
    
        self.__startingForces.setLayout(QVBoxLayout())
        self.__factions.setLayout(QVBoxLayout())
        self.__widget.addWidget(self.__leftTabsWidget)

        self.__startingForces.layout().addWidget(self.__planetComboBox)
        self.__startingForces.layout().addWidget(self.__forcesListTable)
        self.__startingForces.layout().addWidget(self.__planetInfoLabel)
        self.__startingForces.layout().addWidget(self.__importStartingForcesButton)

        self.__factions.layout().addWidget(self.__factionListWidget)

        self.__presenter: MainWindowPresenter = None

    def setMainWindowPresenter(self, presenter: MainWindowPresenter) -> None:
        """Set the presenter class for the window"""
        self.__presenter = presenter

    def getWindow(self) -> QMainWindow:
        """Returns the window"""
        return self.__window

    def emptyWidgets(self) -> None:
        """Clears all list and combobox widgets"""
        self.__GCLayoutWidget.empty()
        self.__factionListWidget.clearContents()
        self.__factionListWidget.setRowCount(0)
        self.__planetComboBox.clear()
        self.__forcesListTable.setModel(None)

    def addPlanets(self, planets: List[str]) -> None:
        """Add Planet objects to the planet table widget"""
        self.__addEntriesToTableWidget(self.__GCLayoutWidget.planetListWidget, planets)
        self.__GCLayoutWidget.planetListWidget.itemClicked.connect(
            self.__onPlanetTableWidgetItemClicked
        )

    def addFactions(self, factions: List[str]) -> None:
        """Add Faction objects to the faction table widget"""
        self.__addEntriesToTableWidget(self.__factionListWidget, factions)
        self.__factionListWidget.itemClicked.connect(
            self.__onFactionTableWidgetItemClicked
        )

    def addTradeRoutes(self, tradeRoutes: List[str]) -> None:
        """Add TradeRoute objects to the trade route table widget"""
        self.__addEntriesToTableWidget(self.__GCLayoutWidget.tradeRouteListWidget, tradeRoutes)

    def updateTradeRoutes(self, tradeRoutes: List[str]) -> None:
        """Update TradeRoute trade route table widget"""
        self.__GCLayoutWidget.tradeRouteListWidget.clearContents()
        self.__GCLayoutWidget.tradeRouteListWidget.setRowCount(0)
        self.__addEntriesToTableWidget(self.__GCLayoutWidget.tradeRouteListWidget, tradeRoutes)

    def addCampaigns(self, campaigns: List[str]) -> None:
        """Add Campaign objects to the campaign combobox widget"""
        self.__GCLayoutWidget.campaignComboBox.addItems(campaigns)
        self.__GCLayoutWidget.campaignComboBox.activated.connect(self.__onCampaignSelected)

    def updatePlanetSelection(self, planets: List[int]) -> None:
        """Clears table, then checks off planets in the table from a list of indexes"""
        checkListTable(self.__GCLayoutWidget.planetListWidget, planets)

    def updateTradeRouteSelection(self, tradeRoutes: List[int]) -> None:
        """Clears table, then checks off trade routes in the table from a list of indexes"""
        checkListTable(self.__GCLayoutWidget.tradeRouteListWidget, tradeRoutes)

    def updateFactionSelection(self, factions: List[int]) -> None:
        """Clears table, then checks off planets in the table from a list of indexes"""
        checkListTable(self.__factionListWidget, factions)

    def updateCampaignComboBoxSelection(self, index: int) -> None:
        """Update selected campaign"""
        self.__GCLayoutWidget.campaignComboBox.setCurrentIndex(index)

    def updatePlanetComboBox(self, planets: List[str]) -> None:
        """Update the planets combobox"""
        self.__planetComboBox.clear()
        if planets:
            if type(planets) == set:
                planets = list(planets)
            planets.sort()
            self.__planetComboBox.addItems(planets)

        self.__planetComboBox.activated.connect(self.__onPlanetSelected)

    def updateCampaignComboBox(self, campaigns: List[str], newCampaign: str) -> None:
        """Update the campaign combobox"""
        self.__GCLayoutWidget.campaignComboBox.clear()
        self.__GCLayoutWidget.campaignComboBox.addItems(campaigns)
        newCampaignIndex = self.__GCLayoutWidget.campaignComboBox.findText(newCampaign)
        self.__GCLayoutWidget.campaignComboBox.setCurrentIndex(newCampaignIndex)
        self.__onCampaignSelected(newCampaignIndex)

    def selectSingleTradeRoute(self, index: int) -> bool:
        """Checks off trade route in the table for an index"""
        if self.__GCLayoutWidget.tradeRouteListWidget.item(index, 0).checkState() == QtCore.Qt.CheckState.Checked:
            self.__GCLayoutWidget.tradeRouteListWidget.item(index, 0).setCheckState(QtCore.Qt.CheckState.Unchecked)
            return False
        else:
            self.__GCLayoutWidget.tradeRouteListWidget.item(index, 0).setCheckState(QtCore.Qt.CheckState.Checked)
            return True

    def updatePlanetCountDisplay(self, planets: List[int]) -> None:
        """Updates count of planets on main window."""
        self.__GCLayoutWidget.planetCountLabel.setText("Planet Count: " + str(len(planets)))

    def updatePlanetInfoDisplay(
        self, planet: Planet, startingForces: pd.DataFrame, filter: str
    ) -> None:
        """Update starting forces and planet info table widget. Starting forces are optional."""

        if startingForces is not None:
            model = PandasModel(startingForces, filter)

            self.__forcesListTable.setModel(model)
        else:
            model = PandasModel(
                pd.DataFrame(
                    columns=["Planet", "Era", "Owner", "ObjectType", "Amount"]
                ),
                False,
            )

            self.__forcesListTable.setModel(model)
            self.__forcesListTable.resizeColumnsToContents()

        self.__planetInfoLabel.setText(
            "Max starbase level: "
            + str(planet.starbaseLevel)
            + "\nSpace structure slots: "
            + str(planet.spaceStructureSlots)
            + "\nGround structure slots: "
            + str(planet.groundStructureSlots)
        )

    def makeGalacticPlot(self) -> GalacticPlot:
        """Plot planets and trade routes"""
        plot: QtGalacticPlot = QtGalacticPlot(self.__widget)
        self.__widget.addWidget(plot.getWidget())
        return plot

    def __addEntriesToTableWidget(
        self, widget: QTableWidget, entries: List[str]
    ) -> None:
        """Adds a list of rows to a table widget with checkboxes"""
        for entry in entries:
            rowCount = widget.rowCount()
            widget.setRowCount(rowCount + 1)
            item: QTableWidgetItem = QTableWidgetItem(entry)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            widget.setItem(rowCount, 0, item)

    def __onPlanetTableWidgetItemClicked(self, item: QTableWidgetItem) -> None:
        """If a planet table widget item is clicked, check it and call the presenter to display it"""
        checked: bool = False
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            checked = True

        self.__presenter.onPlanetChecked(item.row(), checked)

    def __onFactionTableWidgetItemClicked(self, item: QTableWidgetItem) -> None:
        """If a faction table widget item is clicked, check it and call the presenter to add it to the campaign"""
        checked: bool = False
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            checked = True

        self.__presenter.onFactionChecked(item.row(), checked)
        
    def __showAutoConnectionSettings(self) -> None:
        self.__presenter.autoConnectionSettingsCommand.execute()

    def __showPlanetContextMenu(self, position) -> None:
        self.__presenter.planetContextMenu.show(
            self.__GCLayoutWidget.planetListWidget.itemAt(position),
            self.__GCLayoutWidget.planetListWidget.mapToGlobal(position),
        )

    def __onTradeRouteTableWidgetItemClicked(self, item: QTableWidgetItem) -> None:
        """If a trade route table widget item is clicked, check it and call the presenter to display it"""
        checked: bool = False
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            checked = True

        self.__presenter.onTradeRouteChecked(item.row(), checked)

    def __newCampaign(self) -> None:
        """Helper function to launch the new campaign dialog"""
        if self.__presenter is not None:
            # Passes the currently selected campaign text info to the dialog
            self.__presenter.campaignPropertiesCommand.execute()

    def __openFolder(self) -> None:
        """Set data folder dialog"""
        folderName = QFileDialog.getExistingDirectory(
            self.__widget, "Select Data folder:", "", QFileDialog.ShowDirsOnly
        )
        if folderName:
            self.__presenter.onDataFolderChanged(folderName)

    def __newTradeRoute(self) -> None:
        """Helper function to launch the new trade route dialog"""
        if self.__presenter is not None:
            self.__presenter.newTradeRouteCommand.execute()

    def __saveFile(self) -> None:
        """Save file dialog"""
        fileName, _ = QFileDialog.getSaveFileName(
            self.__widget,
            "Save Galactic Conquest",
            "",
            "XML Files (*.xml);;All Files (*)",
        )
        if fileName:
            self.__presenter.saveFile(fileName)

    def __importForcesSaveFile(self) -> None:
        """Import default forces and save"""
        self.__presenter.importStartingForces()
        self.__saveFile()

    def __quit(self) -> None:
        """Exits application by closing the window"""
        self.__window.close()

    def __onCampaignSelected(self, index: int) -> None:
        """Presents a selected campaign"""
        self.__presenter.onCampaignSelected(index)

    def __importStartingForcesButtonClicked(self) -> None:
        """Imports all starting forces from spreadsheets"""
        self.__presenter.importStartingForces()

    def __onPlanetSelected(self, index: int) -> None:
        """Presents a selected planet's starting forces"""
        entry = self.__planetComboBox.currentText()
        self.__presenter.onPlanetSelected(entry)

    def __campaignPropertiesButtonClicked(self) -> None:
        """Helper function to launch the campaign properties dialog"""
        if self.__presenter is not None:
            # Passes the currently selected campaign text info to the dialog
            self.__presenter.campaignPropertiesCommand.execute()
