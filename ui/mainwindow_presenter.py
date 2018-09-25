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
    def makeGalacticPlot(self) -> GalacticPlot:
        raise NotImplementedError()


class MainWindowPresenter:

    def __init__(self, mainWindow: MainWindow, repository: GameObjectRepository):
        self.__mainWindow: MainWindow = mainWindow
        self.__plot: GalacticPlot = self.__mainWindow.makeGalacticPlot()
        self.__repository = repository
        self.__planets: List[Planet] = list(repository.planets)
        self.__tradeRoutes: List[TradeRoute] = list(repository.tradeRoutes)

        self.__mainWindow.addPlanets(self.__getPlanetNames())
        self.__checkedPlanets: Set[Planet] = set()

    def onPlanetChecked(self, index: int, checked: bool) -> None:
        if checked:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__checkedPlanets.add(self.__planets[index])
        else:
            if self.__planets[index] in self.__checkedPlanets:
                self.__checkedPlanets.remove(self.__planets[index])

        self.__plot.plotPlanets(self.__checkedPlanets)

    def __getPlanetNames(self) -> List[str]:
        return [p.name for p in self.__planets]
