from abc import ABC, abstractmethod
from typing import List, Set

import numpy as np
from numpy import ndarray as NumPyArray

from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.faction import Faction
from gameObjects.campaign import Campaign
from ui.galacticplot import GalacticPlot
from RepositoryCreator import RepositoryCreator
from xml.xmlwriter import XMLWriter
from xml.xmlreader import XMLReader


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
    '''Window display class'''
    def __init__(self, mainWindow: MainWindow, repository: GameObjectRepository):
        self.__mainWindow: MainWindow = mainWindow
        self.__plot: GalacticPlot = self.__mainWindow.makeGalacticPlot()
        
        self.__xmlWriter: XMLWriter = XMLWriter()

        self.__repository = repository
        self.__repositoryCreator = RepositoryCreator()

        self.campaigns: List[Campaign] = list()
        self.__planets: List[Planet] = list()
        self.__tradeRoutes: List[TradeRoute] = list()
        self.__availableTradeRoutes: List[TradeRoute] = list()
        self.__newTradeRoutes: List[TradeRoute] = list()

        self.__selectedCampaignIndex: int = 0

        self.__checkedPlanets: Set[Planet] = set()
        self.__checkedTradeRoutes: Set[TradeRoute] = set()

        self.__plot.planetSelectedSignal.connect(self.planetSelectedOnPlot)

        self.__updateWidgets()

        self.newTradeRouteCommand = None
        self.campaignPropertiesCommand = None


    def onDataFolderChanged(self, folder: str) -> None:
        '''Updates the repository and refreshes the main window when a new data folder is selected'''
        self.__repository.emptyRepository()
        self.__repository = self.__repositoryCreator.constructRepository(folder)

        self.__updateWidgets()

    def onPlanetChecked(self, index: int, checked: bool) -> None:
        '''If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot'''
        if checked:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__checkedPlanets.add(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.add(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        else:
            if self.__planets[index] in self.__checkedPlanets:
                self.__checkedPlanets.remove(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.remove(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)
    
    def planetSelectedOnPlot(self, indexes: list) -> None:
        '''If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot'''
        for index in indexes:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__checkedPlanets.add(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.add(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
            elif self.__planets[index] in self.__checkedPlanets:
                self.__checkedPlanets.remove(self.__planets[index])
                self.campaigns[self.__selectedCampaignIndex].planets.remove(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)

        selectedPlanets = []

        for p in self.__checkedPlanets:
            selectedPlanets.append(self.__getNames(self.__planets).index(p.name))

        self.__mainWindow.updatePlanetSelection(selectedPlanets)
        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)
    

    def onTradeRouteChecked(self, index: int, checked: bool) -> None:
        '''If a trade route is checked by the user, add it to the selecte campaign and refresh the galaxy plot'''
        if checked:
            if self.__availableTradeRoutes[index] not in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.add(self.__availableTradeRoutes[index])
                self.campaigns[self.__selectedCampaignIndex].tradeRoutes.add(self.__availableTradeRoutes[index])
        else:
            if self.__availableTradeRoutes[index] in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.remove(self.__availableTradeRoutes[index])
                self.campaigns[self.__selectedCampaignIndex].tradeRoutes.remove(self.__availableTradeRoutes[index])

        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)

    def onCampaignSelected(self, index: int) -> None:
        '''If a campaign is selected by the user, clear then refresh the galaxy plot'''
        self.__checkedPlanets.clear()
        self.__checkedTradeRoutes.clear()

        self.__selectedCampaignIndex = index

        selectedPlanets = []
        selectedTradeRoutes = []

        if self.campaigns[index].planets is not None:
            self.__checkedPlanets.update(self.campaigns[index].planets)

            for p in self.__checkedPlanets:
                selectedPlanets.append(self.__planets.index(p))

            self.__mainWindow.updatePlanetSelection(selectedPlanets)
        
        self.__updateAvailableTradeRoutes(self.campaigns[index].planets)
        
        if self.campaigns[index].tradeRoutes is not None:
            self.__checkedTradeRoutes.update(self.campaigns[index].tradeRoutes)
            
            for t in self.__checkedTradeRoutes:
                selectedTradeRoutes.append(self.__availableTradeRoutes.index(t))

            self.__mainWindow.updateTradeRouteSelection(selectedTradeRoutes)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)

    def onNewCampaign(self, campaign: Campaign) -> None:
        '''If a new campaign is created, add the campaign to the repository, and clear then refresh the galaxy plot'''
        self.__repository.addCampaign(campaign)

        self.__updateWidgets()

        self.__mainWindow.updateCampaignComboBox(self.__getNames(self.campaigns), campaign.name)

    def onNewTradeRoute(self, tradeRoute: TradeRoute):
        '''Handles new trade routes'''
        self.__newTradeRoutes.append(tradeRoute)

        if tradeRoute.start in self.__checkedPlanets or tradeRoute.end in self.__checkedPlanets:
            self.__checkedTradeRoutes.add(tradeRoute)

        self.campaigns[self.__selectedCampaignIndex].tradeRoutes.add(tradeRoute)
        self.__updateWidgets()

    def onPlanetSelected(self, entry: str) -> None:
        '''If a planet is selected by the user, display the associated starting forces'''
        campaignForces = self.campaigns[self.__selectedCampaignIndex].startingForces

        startingForces = []
        for startingForce in campaignForces:
            if startingForce.planet.name == entry:
                fullStartingForce = startingForce.unpack()
                startingForces.append(fullStartingForce[2])

        self.__mainWindow.updateStartingForces(startingForces)
    
    def allPlanetsChecked(self, checked: bool) -> None:
        '''Select all planets handler: plots all planets'''
        if checked:
            self.__checkedPlanets.update(self.__planets)
        else:
            self.__checkedPlanets.clear()

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)    

    def allTradeRoutesChecked(self, checked: bool) -> None:
        '''Select all trade routes handler: plots all trade routes'''
        if checked:
            self.__checkedTradeRoutes.update(self.__availableTradeRoutes)
        else:
            self.__checkedTradeRoutes.clear()

        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)  

    def saveFile(self, fileName: str) -> None:
        '''Saves XML files'''
        campaign = self.campaigns[self.__selectedCampaignIndex]
        self.__xmlWriter.campaignWriter(campaign, fileName)
        if len(self.__newTradeRoutes) > 0:
            self.__xmlWriter.tradeRouteWriter(self.__newTradeRoutes)


    def __getNames(self, inputList: list) -> List[str]:
        '''Returns the name attribute from a list of GameObjects'''
        return [x.name for x in inputList]

    def __updateWidgets(self) -> None:
        '''Update the main window widgets'''
        self.campaigns: List[Campaign] = sorted(self.__repository.campaigns, key = lambda entry: entry.name)
        self.__planets: List[Planet] = sorted(self.__repository.planets, key = lambda entry: entry.name)
        self.__tradeRoutes: List[TradeRoute] = sorted(self.__repository.tradeRoutes, key = lambda entry: entry.name)
        self.__factions: List[Faction] = sorted(self.__repository.factions, key = lambda entry: entry.name)

        self.__updateAvailableTradeRoutes(self.campaigns[self.__selectedCampaignIndex].planets)

        self.__mainWindow.emptyWidgets()

        self.__mainWindow.addCampaigns(self.__getNames(self.campaigns))
        self.__mainWindow.addPlanets(self.__getNames(self.__planets))
        self.__mainWindow.addTradeRoutes(self.__getNames(self.__availableTradeRoutes))

        self.__mainWindow.updateCampaignComboBoxSelection(self.__selectedCampaignIndex)
        self.onCampaignSelected(self.__selectedCampaignIndex)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))

        if self.__getSelectedTradeRouteIndices():
            self.__mainWindow.updateTradeRouteSelection(self.__getSelectedTradeRouteIndices())

        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)
        
    def __getSelectedTradeRouteIndices(self) -> List[int]:
        '''Returns the indices of selected trade routes'''
        selectedTradeRoutesIndices: List[int] = list()
        for tradeRoute in self.__checkedTradeRoutes:
            selectedTradeRoutesIndices.append(self.__availableTradeRoutes.index(tradeRoute))

        return selectedTradeRoutesIndices

    def __updateAvailableTradeRoutes(self, planetList:  list):
        '''Updates the list of available trade routes based on the planets in the GC'''
        privateAvailableTradeRoutes = set()

        if planetList is not None:
            for planet in planetList:
                for route in self.__tradeRoutes:
                    if route.start == planet or route.end == planet:
                        privateAvailableTradeRoutes.add(route)

        self.__availableTradeRoutes = sorted(privateAvailableTradeRoutes, key = lambda entry: entry.name)

        self.__mainWindow.updateTradeRoutes(self.__getNames(self.__availableTradeRoutes))