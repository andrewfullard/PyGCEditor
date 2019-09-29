from math import sqrt
'''Planet class definition'''


class Planet:
    '''Planets have a name and location (x, y), and starting forces'''
    def __init__(self, name: str):
        self.__name: str = name
        self.__variantOf: str = ""
        self.__x: float = 0.0
        self.__y: float = 0.0
        self.__forces: list = []
    
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
    def forces(self) -> list:
        return self.__forces

    @forces.setter
    def forces(self, value: list) -> None:
        self.__forces = value
