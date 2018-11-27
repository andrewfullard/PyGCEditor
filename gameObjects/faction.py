'''Faction class definition'''
from gameObjects.planet import Planet
from gameObjects.aiplayer import AIPlayer

class Faction:
    '''Factions have a name, capital planet, and AI'''
    def __init__(self, name: str):
        self.__name: str = name
        self.__capital: Planet = None
        self.__aiplayer: AIPlayer = None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self.__name = value

    @property
    def capital(self) -> Planet:
        return self.__capital

    @capital.setter
    def capital(self, value: Planet) -> None:
        if value is not None:
            self.__capital = value

    @property
    def aiplayer(self) -> AIPlayer:
        return self.__aiplayer

    @aiplayer.setter
    def aiplayer(self, value: AIPlayer) -> None:
        if value is not None:
            self.__aiplayer = value
