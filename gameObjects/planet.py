'''Planet class definition'''


class Planet:
    '''Planets have a name and location (x, y), starbase level, and special structure slots'''
    def __init__(self, name: str):
        self.__name: str = name
        self.__x: float = 0.0
        self.__y: float = 0.0
        self.__starbaseLevel: int = 0
        self.__spaceStructureSlots: int = 0
        self.__groundStructureSlots: int = 0

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self.__name = value

    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, value: float) -> None:
        self.__x = value

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value: float) -> None:
        self.__y = value

    @property
    def starbaseLevel(self) -> int:
        return self.__starbaseLevel

    @starbaseLevel.setter
    def starbaseLevel(self, value: int) -> None:
        self.__starbaseLevel = value

    @property
    def spaceStructureSlots(self) -> int:
        return self.__spaceStructureSlots

    @spaceStructureSlots.setter
    def spaceStructureSlots(self, value: int) -> None:
        self.__spaceStructureSlots = value
    
    @property
    def groundStructureSlots(self) -> int:
        return self.__groundStructureSlots

    @groundStructureSlots.setter
    def groundStructureSlots(self, value: int) -> None:
        self.__groundStructureSlots = value