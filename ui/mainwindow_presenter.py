from abc import ABC, abstractmethod
from typing import List, Set, Dict

import numpy as np
from numpy import ndarray as NumPyArray

from config import Config
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.faction import Faction
from gameObjects.campaign import Campaign
from ui.galacticplot import GalacticPlot
from RepositoryCreator import RepositoryCreator
from xmlUtil.xmlwriter import XMLWriter
from xmlUtil.xmlreader import XMLReader
from xmlUtil.xmlstructure import XMLStructure


class MainWindowPresenter:
    pass


class MainWindow(ABC):
    @abstractmethod
    def setMainWindowPresenter(self, presenter: MainWindowPresenter) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addPlanets(self, planets: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addTradeRoutes(self, tradeRoutes: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addCampaigns(self, campaigns: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def makeGalacticPlot(self) -> GalacticPlot:
        raise NotImplementedError()

    @abstractmethod
    def emptyWidgets(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateCampaignComboBox(self, campaigns: List[str], newCampaign: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateCampaignComboBoxSelection(self, index: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updatePlanetComboBox(self, planets: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updatePlanetSelection(self, planets: List[Planet]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateTradeRouteSelection(self, tradeRoutes: List[TradeRoute]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def clearPlanets(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def clearTradeRoutes(self) -> None:
        raise NotImplementedError()


class MainWindowPresenter:
    """Window display class"""

    def __init__(
        self, mainWindow: MainWindow, repository: GameObjectRepository, config: Config
    ):
        self.__mainWindow: MainWindow = mainWindow
        self.__plot: GalacticPlot = self.__mainWindow.makeGalacticPlot()

        self.__xmlWriter: XMLWriter = XMLWriter()

        self.__repository = repository
        self.__repositoryCreator = RepositoryCreator()

        self.__config = config

        self.campaigns: List[Campaign] = list()
        self.__planets: List[Planet] = list()
        self.__tradeRoutes: List[TradeRoute] = list()
        self.__availableTradeRoutes: List[TradeRoute] = list()
        self.__newTradeRoutes: List[TradeRoute] = list()
        self.__updatedPlanetCoords: Dict[str, List[float]] = dict()

        self.__selectedCampaignIndex: int = 0

        self.__checkedPlanets: Set[Planet] = set()
        self.__checkedTradeRoutes: Set[TradeRoute] = set()

        self.__showAutoConnections = True

        self.__plot.planetSelectedSignal.connect(self.planetSelectedOnPlot)

        self.__updateWidgets()

        self.newTradeRouteCommand = None
        self.campaignPropertiesCommand = None

    def onDataFolderChanged(self, folder: str) -> None:
        """Updates the repository and refreshes the main window when a new data folder is selected"""
        self.__repository.emptyRepository()
        self.__repository = self.__repositoryCreator.constructRepository(folder)
        XMLStructure.dataFolder = folder

        self.__updateWidgets()

    def onPlanetChecked(self, index: int, checked: bool) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        if checked:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__checkedPlanets.add(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.add(
                    self.__planets[index]
                )
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        else:
            if self.__planets[index] in self.__checkedPlanets:
                self.__checkedPlanets.remove(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.remove(
                    self.__planets[index]
                )
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__updateGalacticPlot()

    def planetSelectedOnPlot(self, indexes: list) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        for index in indexes:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__checkedPlanets.add(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.add(
                    self.__planets[index]
                )
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
            elif self.__planets[index] in self.__checkedPlanets:
                self.__checkedPlanets.remove(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.remove(
                    self.__planets[index]
                )
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)

        selectedPlanets = []

        for p in self.__checkedPlanets:
            selectedPlanets.append(self.__getNames(self.__planets).index(p.name))

        self.__mainWindow.updatePlanetSelection(selectedPlanets)
        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__updateGalacticPlot()

    def onTradeRouteChecked(self, index: int, checked: bool) -> None:
        """If a trade route is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        if checked:
            if self.__availableTradeRoutes[index] not in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.add(self.__availableTradeRoutes[index])
                self.campaigns[self.__selectedCampaignIndex].tradeRoutes.add(
                    self.__availableTradeRoutes[index]
                )
        else:
            if self.__availableTradeRoutes[index] in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.remove(self.__availableTradeRoutes[index])
                self.campaigns[self.__selectedCampaignIndex].tradeRoutes.remove(
                    self.__availableTradeRoutes[index]
                )

        self.__updateGalacticPlot()

    def onCampaignSelected(self, index: int) -> None:
        """If a campaign is selected by the user, clear then refresh the galaxy plot"""
        self.__checkedPlanets.clear()
        self.__checkedTradeRoutes.clear()

        self.__selectedCampaignIndex = index

        if self.campaigns[index].planets is not None:
            self.__updateSelectedPlanets(index)

        self.__updateAvailableTradeRoutes(self.campaigns[index].planets)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__updateGalacticPlot()

    def onNewCampaign(self, campaign: Campaign) -> None:
        """If a new campaign is created, add the campaign to the repository, and clear then refresh the galaxy plot"""
        self.__repository.addCampaign(campaign)

        self.__updateWidgets()

        self.__mainWindow.updateCampaignComboBox(
            self.__getNames(self.campaigns), campaign.name
        )

    def onNewTradeRoute(self, tradeRoute: TradeRoute):
        """Handles new trade routes"""
        self.__repository.addTradeRoute(tradeRoute)
        self.__newTradeRoutes.append(tradeRoute)

        if (
            tradeRoute.start in self.__checkedPlanets
            or tradeRoute.end in self.__checkedPlanets
        ):
            self.__checkedTradeRoutes.add(tradeRoute)

        self.campaigns[self.__selectedCampaignIndex].tradeRoutes.add(tradeRoute)
        self.__updateWidgets()

    def onAutoConnectionSettingChanged(
        self, newAutoConnectionDistance, showAutoConnections
    ):
        self.__config.autoPlanetConnectionDistance = newAutoConnectionDistance
        self.__showAutoConnections = showAutoConnections
        self.__updateGalacticPlot()

    def onPlanetPositionChanged(self, name, new_x, new_y) -> None:
        """Updates position of a planet in the repository"""
        planet = self.__repository.getPlanetByName(name)
        planet.x = new_x
        planet.y = new_y
        self.__updatedPlanetCoords[name] = [new_x, new_y]
        self.__updateGalacticPlot()

    def allPlanetsChecked(self, checked: bool) -> None:
        """Select all planets handler: plots all planets"""
        if checked:
            self.__checkedPlanets.update(self.__planets)
            self.campaigns[self.__selectedCampaignIndex].planets.update(
                self.__availableTradeRoutes
            )
        else:
            self.__checkedPlanets.clear()
            self.campaigns[self.__selectedCampaignIndex].planets.clear()

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        self.__updateGalacticPlot()

    def allTradeRoutesChecked(self, checked: bool) -> None:
        """Select all trade routes handler: plots all trade routes"""
        if checked:
            self.__checkedTradeRoutes.update(self.__availableTradeRoutes)
            self.campaigns[self.__selectedCampaignIndex].tradeRoutes.update(
                self.__availableTradeRoutes
            )
        else:
            self.__checkedTradeRoutes.clear()
            self.campaigns[self.__selectedCampaignIndex].tradeRoutes.clear()

        self.__updateGalacticPlot()

    def saveFile(self, fileName: str) -> None:
        """Saves XML files"""
        campaign = self.campaigns[self.__selectedCampaignIndex]
        self.__xmlWriter.campaignWriter(campaign, fileName)

        if len(self.__newTradeRoutes) > 0:
            self.__xmlWriter.tradeRouteWriter(self.__newTradeRoutes)

        if len(self.__updatedPlanetCoords) > 0:
            xmlReader = XMLReader()
            gameObjectFile = XMLStructure.dataFolder + "/XML/GameObjectFiles.XML"
            planetRoots = xmlReader.findPlanetFilesAndRoots(gameObjectFile)
            self.__xmlWriter.planetCoordinatesWriter(
                XMLStructure.dataFolder + "/XML/",
                planetRoots,
                self.__updatedPlanetCoords,
            )

    def getNameOfPlanetAt(self, ind: int) -> str:
        return self.__planets[ind].name

    def getPositionOfPlanetAt(self, ind: int):
        return self.__planets[ind].x, self.__planets[ind].y

    def __getNames(self, inputList: list) -> List[str]:
        """Returns the name attribute from a list of GameObjects"""
        return [x.name for x in inputList]

    def __updateWidgets(self) -> None:
        """Update the main window widgets"""
        self.campaigns: List[Campaign] = sorted(
            self.__repository.campaigns, key=lambda entry: entry.name
        )
        self.__planets: List[Planet] = sorted(
            self.__repository.planets, key=lambda entry: entry.name
        )
        self.__tradeRoutes: List[TradeRoute] = sorted(
            self.__repository.tradeRoutes, key=lambda entry: entry.name
        )
        self.__factions: List[Faction] = sorted(
            self.__repository.factions, key=lambda entry: entry.name
        )

        self.__updateAvailableTradeRoutes(
            self.campaigns[self.__selectedCampaignIndex].planets
        )

        self.__mainWindow.emptyWidgets()

        self.__mainWindow.addCampaigns(self.__getNames(self.campaigns))
        self.__mainWindow.addPlanets(self.__getNames(self.__planets))
        self.__mainWindow.addTradeRoutes(self.__getNames(self.__availableTradeRoutes))

        self.__mainWindow.updateCampaignComboBoxSelection(self.__selectedCampaignIndex)
        self.onCampaignSelected(self.__selectedCampaignIndex)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))

        self.__updateSelectedTradeRoutes(self.__selectedCampaignIndex)

        self.__updateGalacticPlot()

    def __updateSelectedPlanets(self, index: int) -> None:
        """Update the selected trade routes for the currently selected campaign"""
        selectedPlanets = []

        self.__checkedPlanets.update(self.campaigns[index].planets)

        for p in self.__checkedPlanets:
            selectedPlanets.append(self.__planets.index(p))

        self.__mainWindow.updatePlanetSelection(selectedPlanets)

    def __updateSelectedTradeRoutes(self, index: int) -> None:
        """Update the selected planets for the currently selected campaign"""
        selectedTradeRoutes = []

        self.__checkedTradeRoutes = self.campaigns[index].tradeRoutes.intersection(
            self.__availableTradeRoutes
        )

        for t in self.__checkedTradeRoutes:
            selectedTradeRoutes.append(self.__availableTradeRoutes.index(t))

        self.__mainWindow.updateTradeRouteSelection(selectedTradeRoutes)

    def __updateAvailableTradeRoutes(self, planetList: list):
        """Updates the list of available trade routes based on the planets in the GC"""
        privateAvailableTradeRoutes = set(
            filter(
                lambda tr: (tr.start in planetList and tr.end in planetList),
                self.__tradeRoutes,
            )
        )

        if len(self.__newTradeRoutes) > 0:
            # Ensure any new routes are appended to the available list for immediate use
            privateAvailableTradeRoutes.update(self.__newTradeRoutes)

        self.campaigns[self.__selectedCampaignIndex].tradeRoutes = self.campaigns[
            self.__selectedCampaignIndex
        ].tradeRoutes.intersection(privateAvailableTradeRoutes)

        self.__availableTradeRoutes = sorted(
            privateAvailableTradeRoutes, key=lambda entry: entry.name
        )
        self.__mainWindow.updateTradeRoutes(
            self.__getNames(self.__availableTradeRoutes)
        )
        self.__updateSelectedTradeRoutes(self.__selectedCampaignIndex)

    def __updateGalacticPlot(self):
        autoConnectionDistance = self.config.autoPlanetConnectionDistance
        if not self.__showAutoConnections:
            autoConnectionDistance = 0
        self.__plot.plotGalaxy(
            self.__checkedPlanets,
            self.__checkedTradeRoutes,
            self.__planets,
            autoConnectionDistance,
        )

    @property
    def config(self):
        return self.__config

    @property
    def showAutoConnections(self):
        return self.__showAutoConnections
