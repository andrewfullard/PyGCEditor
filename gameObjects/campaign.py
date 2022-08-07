from typing import Set
from typing import List
import pandas as pd

from gameObjects.planet import Planet
from gameObjects.faction import Faction
from gameObjects.traderoute import TradeRoute
from gameObjects.startingForce import StartingForce

"""Campaign class definition"""


class Campaign:
    """Campaigns have a name, set name, planets and traderoutes"""

    def __init__(self, name: str = ""):
        self.__name: str = name
        self.__setName: str = "Empty"
        self.__sortOrder: str = "0"
        self.__textID: str = "MISSING"
        self.__descriptionText: str = "MISSING"
        self.__startingActivePlayer: str = "Rebel"
        self.__rebelStoryName: str = ""
        self.__empireStoryName: str = ""
        self.__underworldStoryName: str = ""
        self.__eraStart: str = "0"
        self.__era = 1

        self.__planets: Set[Planet] = set()
        self.__playableFactions: Set[Faction] = set()
        self.__tradeRoutes: Set[TradeRoute] = set()
        self.startingForces = pd.DataFrame()

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
    def sortOrder(self) -> str:
        return self.__sortOrder

    @sortOrder.setter
    def sortOrder(self, value: str) -> None:
        if value:
            self.__sortOrder = value

    @property
    def textID(self) -> str:
        return self.__textID

    @textID.setter
    def textID(self, value: str) -> None:
        if value:
            self.__textID = value

    @property
    def descriptionText(self) -> str:
        return self.__descriptionText

    @descriptionText.setter
    def descriptionText(self, value: str) -> None:
        if value:
            self.__descriptionText = value

    @property
    def startingActivePlayer(self) -> str:
        return self.__startingActivePlayer

    @startingActivePlayer.setter
    def startingActivePlayer(self, value: str) -> None:
        if value:
            self.__startingActivePlayer = value

    @property
    def rebelStoryName(self) -> str:
        return self.__rebelStoryName

    @rebelStoryName.setter
    def rebelStoryName(self, value: str) -> None:
        if value:
            self.__rebelStoryName = value

    @property
    def empireStoryName(self) -> str:
        return self.__empireStoryName

    @empireStoryName.setter
    def empireStoryName(self, value: str) -> None:
        if value:
            self.__empireStoryName = value

    @property
    def underworldStoryName(self) -> str:
        return self.__underworldStoryName

    @underworldStoryName.setter
    def underworldStoryName(self, value: str) -> None:
        if value:
            self.__underworldStoryName = value

    @property
    def eraStart(self) -> str:
        return self.__eraStart

    @eraStart.setter
    def eraStart(self, value: str) -> None:
        if value:
            self.__eraStart = value

    @property
    def planets(self) -> Set[Planet]:
        return self.__planets

    @planets.setter
    def planets(self, value: Set[Planet]) -> None:
        if value:
            self.__planets = value

    @property
    def playableFactions(self) -> Set[Faction]:
        return self.__playableFactions

    @playableFactions.setter
    def playableFactions(self, value: Set[Faction]) -> None:
        if value:
            self.__playableFactions = value

    @property
    def tradeRoutes(self) -> Set[TradeRoute]:
        return self.__tradeRoutes

    @tradeRoutes.setter
    def tradeRoutes(self, value: Set[TradeRoute]) -> None:
        if value:
            self.__tradeRoutes = value

    @property
    def era(self) -> int:
        return self.__era
