from itertools import groupby
from typing import TYPE_CHECKING, List, Set

from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.startingForce import StartingForce
from gameObjects.traderoute import TradeRoute

from util import getObject


class DisplayHelpers:
    """Helper functions for  retrieving information for display"""

    def __init__(self, repository: GameObjectRepository, campaigns: List[Campaign]):
        self.repository = repository
        self.campaigns = campaigns

    def getPlanetOwners(self, index: int, planetList: List[Planet]) -> List[Faction]:
        """Gets a list of owners of planets in the GC selected by index"""
        owners_names = []
        owners = []
        for planet in planetList:
            owners.append(
                self.__getPlanetOwner(index, planet.name, self.campaigns[index].era)
            )

        return owners

    def __getPlanetOwner(self, index: int, planet: str, era: int) -> Faction:
        """Gets the owner of a planet in the GC selected by index and era"""

        try:
            sf = self.campaigns[index].startingForces
            planet_info = sf.loc[(sf.Planet == planet)].groupby(sf.Planet).head(1)
        except KeyError:
            return self.__getNeutralFaction()

        try:
            faction_name = planet_info.values[0][2]
        except IndexError:
            return self.__getNeutralFaction()

        return getObject(faction_name, self.repository.factions)

    def __getNeutralFaction(self) -> Faction:
        """Gets the Neutral faction entry, if possible"""
        for faction in self.repository.factions:
            if faction.name == "Neutral":
                return faction

        print("Error! Neutral faction not found!")
