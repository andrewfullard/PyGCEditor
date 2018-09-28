from abc import ABC, abstractmethod
from typing import List

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute


class GalacticPlot(ABC):

    @abstractmethod
    def plotPlanets(self, planets: List[Planet]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def plotTradeRoutes(self, tradeRoutes: List[TradeRoute]) -> None:
        raise NotImplementedError()
