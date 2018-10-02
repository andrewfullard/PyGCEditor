from abc import ABC, abstractmethod
from typing import List, Set

import numpy as np
from numpy import ndarray as NumPyArray

from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from ui.galacticplot import GalacticPlot


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


class MainWindowPresenter:

    def __init__(self, mainWindow: MainWindow, repository: GameObjectRepository):
        self.__mainWindow: MainWindow = mainWindow
        self.__plot: GalacticPlot = self.__mainWindow.makeGalacticPlot()
        self.__repository = repository
        self.__campaigns: List[Campaign] = sorted(repository.campaigns, key = lambda entry: entry.name)
        self.__planets: List[Planet] = sorted(repository.planets, key = lambda entry: entry.name)
        self.__tradeRoutes: List[TradeRoute] = sorted(repository.tradeRoutes, key = lambda entry: entry.name)

        self.__mainWindow.addCampaigns(self.__getNames(self.__campaigns))
        self.__mainWindow.addPlanets(self.__getNames(self.__planets))
        self.__mainWindow.addTradeRoutes(self.__getNames(self.__tradeRoutes))
        self.__checkedPlanets: Set[Planet] = set()
        self.__checkedTradeRoutes: Set[TradeRoute] = set()

    def onPlanetChecked(self, index: int, checked: bool) -> None:
        if checked:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__checkedPlanets.add(self.__planets[index])
        else:
            if self.__planets[index] in self.__checkedPlanets:
                self.__checkedPlanets.remove(self.__planets[index])

        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)
    
    def onTradeRouteChecked(self, index: int, checked: bool) -> None:
        if checked:
            if self.__tradeRoutes[index] not in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.add(self.__tradeRoutes[index])
        else:
            if self.__tradeRoutes[index] in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.remove(self.__tradeRoutes[index])

        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)
    
    def allPlanetsChecked(self, checked: bool) -> None:
        if checked:
            self.__checkedPlanets.update(self.__planets)
        else:
            self.__checkedPlanets.clear()

        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)    

    def allTradeRoutesChecked(self, checked: bool) -> None:
        if checked:
            self.__checkedTradeRoutes.update(self.__tradeRoutes)
        else:
            self.__checkedTradeRoutes.clear()

        self.__plot.plotGalaxy(self.__checkedPlanets, self.__checkedTradeRoutes, self.__planets)        

    def __getNames(self, inputList: list) -> List[str]:
        return [x.name for x in inputList]
