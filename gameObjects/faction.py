'''Faction class definition'''
from gameObjects.planet import Planet
from gameObjects.aiplayer import AIPlayer

class Faction:
    '''Factions have a name, capital planet, AI, and color'''
    def __init__(self, name: str):
        self.__name: str = name
        self.__capital: Planet = None
        self.__aiplayer: AIPlayer = None
        self.__color: list = [0, 0, 0, 0]
        self.__playable: bool = True
        #self.__story: str = story 

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

    @property
    def color(self) -> list():
        return self.__color

    @color.setter
    def color(self, value: list) -> None:
        if value is not None:
            self.__color = value

    @property
    def playable(self) -> list():
        return self.__playable

    @playable.setter
    def playable(self, value: bool) -> None:
        if value is not None:
            self.__playable = value

    # @property
    # def story(self) -> str:
    #     return self.__story

    # @story.setter
    # def story(self, value: str) -> None:
    #     if value:
    #         self.__story = value
