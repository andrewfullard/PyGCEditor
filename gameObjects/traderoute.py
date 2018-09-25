from gameObjects.planet import Planet
'''Trade route class definition'''


class TradeRoute:
    '''Trade routes have a name and a start/end planet
    this doc will be better once I get better at it'''
    def __init__(self, name: str):
        self.__name: str = ""
        self.__start: Planet = None
        self.__end: Planet = None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self.__name

    @property
    def start(self) -> Planet:
        return self.__start

    @start.setter
    def start(self, value: Planet) -> None:
        if value is not None:
            self.__start = value

    @property
    def end(self) -> Planet:
        return self.__end

    @end.setter
    def end(self, value: Planet) -> None:
        if value is not None:
            self.__end = value
