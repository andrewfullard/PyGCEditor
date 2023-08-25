from math import sqrt
'''Planet class definition'''


class Planet:
    '''Planets have a name and location (x, y), starbase level, shipyard and special structure slots'''
    def __init__(self, name: str):
        self.__name: str = name
        self.__variantOf: str = ""
        self.__x: float = 0.0
        self.__y: float = 0.0
        self.__starbaseLevel: int = 0
        self.__spaceStructureSlots: int = 0
        self.__shipyardLevel: str = ""
        self.__SupportsStructure: str = ""
        self.__groundStructureSlots: int = 0
        self.__income: int = 0
    
    def distanceTo(self, target):
        return sqrt((self.x - target.x)**2 + (self.y - target.y)**2)
        

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self.__name = value

    @property
    def variantOf(self) -> str:
        return self.__variantOf

    @variantOf.setter
    def variantOf(self, value: str) -> None:
        if value:
            self.__variantOf = value

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
    def shipyardLevel(self) -> str:
        return self.__shipyardLevel

    @shipyardLevel.setter
    def shipyardLevel(self, value: str) -> None:
        if value:
            self.__shipyardLevel = value
    
    @property
    def SupportsStructure(self) -> str:
        return self.__SupportsStructure

    @SupportsStructure.setter
    def SupportsStructure(self, value: str) -> None:
        if value:
            self.__SupportsStructure = value
    
    @property
    def groundStructureSlots(self) -> int:
        return self.__groundStructureSlots

    @groundStructureSlots.setter
    def groundStructureSlots(self, value: int) -> None:
        self.__groundStructureSlots = value

    @property
    def income(self) -> int:
        return self.__income

    @income.setter
    def income(self, value: int) -> None:
        self.__income = value
