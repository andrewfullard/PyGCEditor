from typing import Set
from typing import List

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.startingForce import StartingForce

'''Campaign class definition'''
class Campaign:
    '''Campaigns have a name, set name, planets and traderoutes'''
    def __init__(self, name: str):
        self.__name: str = name
        self.__setName: str = "Empty"
        self.__planets: Set[Planet] = set()
        self.__tradeRoutes: Set[TradeRoute] = set()
        self.__startingForces: List[StartingForce] = list()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self.__name = value

    @property
    def setName(self) -> str:
        return self.__setName

    @setName.setter
    def setName(self, value: str) -> None:
        if value:
            self.__setName = value

    @property
    def planets(self) -> Set[Planet]:
        return self.__planets

    @planets.setter
    def planets(self, value: Set[Planet]) -> None:
        if value:
            self.__planets = value

    @property
    def tradeRoutes(self) -> Set[TradeRoute]:
        return self.__tradeRoutes

    @tradeRoutes.setter
    def tradeRoutes(self, value: Set[TradeRoute]) -> None:
        if value:
            self.__tradeRoutes = value

    @property
    def startingForces(self) -> List[StartingForce]:
        return self.__startingForces

    @startingForces.setter
    def startingForces(self, value: List[StartingForce]) -> None:
        if value:
            self.__startingForces = value