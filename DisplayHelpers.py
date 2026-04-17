from typing import Iterable

import pandas as pd

from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet

from util import getObject


class DisplayHelpers:
    """Helper functions for  retrieving information for display"""

    def __init__(self, repository: GameObjectRepository, campaigns: list[Campaign]):
        self.repository = repository
        self.campaigns = campaigns

    def getPlanetOwners(self, index: int, planetList: set[Planet]) -> list[Faction]:
        """Gets a list of owners of planets in the GC selected by index"""
        owners = []
        for planet in planetList:
            owners.append(
                self.__getPlanetOwner(index, planet.name, self.campaigns[index].era)
            )

        return owners

    def __getPlanetOwner(self, index: int, planet: str, era: int) -> Faction:
        """Gets the owner of a planet in the GC selected by index and era"""

        sf = self.campaigns[index].startingForces
        if sf is None:
            return self.__getNeutralFaction()

        try:
            planet_info = sf.loc[(sf.Planet.str.lower() == planet.lower()) & (sf.Era == era)]
        except KeyError:
            return self.__getNeutralFaction()

        try:
            planet_info = sf.loc[(sf.Planet.str.lower() == planet.lower())]
        except KeyError:
            return self.__getNeutralFaction()

        try:
            faction_name = planet_info.values[0][2]
        except IndexError:
            return self.__getNeutralFaction()

        faction = getObject(faction_name, self.repository.factions)

        if faction is not None:
            return faction
        else:
            return self.__getNeutralFaction()

    def __getNeutralFaction(self) -> Faction:
        """Gets the Neutral faction entry, if possible"""
        for faction in self.repository.factions:
            if faction.name == "Neutral":
                return faction

        raise RuntimeError("Error! Neutral faction not found!")

    def calculateFactionIncome(
        self, planets: Iterable[Planet], planet_owners: Iterable[Faction | None]
    ) -> dict:
        """Calculates per-faction planet totals and income totals."""
        incomes = []
        factions = []
        owners = list(planet_owners)

        for p in planets:
            incomes.append(p.income)
        for f in owners:
            if f:
                factions.append(f.name)
            else:
                factions.append("None")

        if len(owners) == 0:
            return {}

        df = pd.DataFrame({"income": incomes, "Faction": factions})
        totals = df.groupby("Faction").agg(
            income=("income", "sum"),
            planets=("Faction", "size"),
        )

        return totals.to_dict(orient="index")
