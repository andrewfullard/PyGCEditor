from typing import List

from gameObjects.planet import Planet
from gameObjects.faction import Faction

"""Starting Forces class definition"""


class StartingForce:
    """Starting Forces have a planet, faction and unit"""

    def __init__(self, planet: Planet, faction: Faction, unit: str):
        self.__planet: Planet = planet
        self.__faction: Faction = faction
        self.__unit: str = unit

    def unpack(self) -> List[str]:
        return [self.__faction.name, self.__planet.name, self.__unit]

    @property
    def planet(self) -> Planet:
        return self.__planet

    @planet.setter
    def planet(self, value: Planet) -> None:
        if value:
            self.__planet = value

    @property
    def faction(self) -> Faction:
        return self.__faction

    @faction.setter
    def faction(self, value: Faction) -> None:
        if value:
            self.__faction = value

    @property
    def unit(self) -> str:
        return self.__unit

    @unit.setter
    def unit(self, value: str) -> None:
        if value:
            self.__unit = value
