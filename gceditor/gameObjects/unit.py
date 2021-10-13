'''Unit class definition'''


class Unit:
    '''Units have a name'''
    def __init__(self, name: str):
        self.__name: str = name

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self.__name = value