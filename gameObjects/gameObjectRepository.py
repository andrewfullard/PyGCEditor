from typing import Set

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute


class GameObjectRepository:

    def __init__(self):
        self.__planets: Set[Planet] = set()
        self.__tradeRoutes: Set[TradeRoute] = set()

    def addPlanet(self, planet: Planet) -> None:
        self.__planets.add(planet)

    def removePlanet(self, planet: Planet) -> None:
        self.__planets.remove(planet)

    def addTradeRoute(self, tradeRoute: TradeRoute) -> None:
        self.__tradeRoutes.add(tradeRoute)

    def removeTradeRoute(self, tradeRoute: TradeRoute) -> None:
        self.__tradeRoutes.remove(tradeRoute)

    @property
    def planets(self) -> Set[Planet]:
        return set(self.__planets)

    @property
    def tradeRoutes(self) -> Set[TradeRoute]:
        return set(self.__tradeRoutes)
