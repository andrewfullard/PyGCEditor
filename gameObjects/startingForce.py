from typing import List

from gameObjects.planet import Planet
from gameObjects.unit import Unit
from gameObjects.faction import Faction

'''Starting Forces class definition'''
class StartingForce:
    '''Starting Forces have a planet, faction and unit'''
    def __init__(self, planet: Planet, faction: Planet, unit: Planet):
        self.__planet: Planet = planet
        self.__faction: Faction = faction
        self.__unit: Unit = unit
    
    def unpack(self) -> List[str]:
        return [self.__faction.name, self.__planet.name, self.__unit.name]

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
    def unit(self) -> Unit:
        return self.__unit

    @unit.setter
    def unit(self, value: Unit) -> None:
        if value:
            self.__unit = value