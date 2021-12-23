from itertools import groupby
from typing import TYPE_CHECKING, List, Set

from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.startingForce import StartingForce
from gameObjects.traderoute import TradeRoute
from gameObjects.unit import Unit

from util import getObject


class DisplayHelpers:
    """Helper functions for  retrieving information for display"""

    def __init__(self, repository: GameObjectRepository, campaigns: List[Campaign]):
        self.repository = repository
        self.campaigns = campaigns

    """
    def calculateForcesSum(self, index: int) -> str:
        '''Calculates the total forces of a given faction in the map, and returns them as a text string for display'''
        factionForces = []
        
        for faction, group in groupby(self.__sortInput(index), key = lambda entry: entry.faction):
            factionPower = 0
            for entry in group:
                if entry is not None:
                    if entry.unit is not None:
                        factionPower += entry.unit.combatPower
            factionForces.append([faction, factionPower])

        totalForcesText = ""
        for entry in factionForces:
            totalForcesText += entry[0].name + ": " + str(entry[1]) +", "

        return totalForcesText
    """

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
            planet_info = self.campaigns[index].startingForces["Planet"][planet]
        except KeyError:
            return self.__getNeutralFaction()

        return planet_info["Era"].values[0]

    def __getNeutralFaction(self) -> Faction:
        """Gets the Neutral faction entry, if possible"""
        for faction in self.repository.factions:
            if faction.name == "Neutral":
                return faction

        print("Error! Neutral faction not found!")

    def __sortInput(self, index: int) -> List[StartingForce]:
        return sorted(
            self.campaigns[index].startingForces, key=lambda entry: entry.faction.name
        )
