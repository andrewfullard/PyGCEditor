'''Unit class definition'''


class Unit:
    '''Units have a name'''
    def __init__(self, name: str):
        self.__name: str = name
        self.__combatPower: str = '0'

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self.__name = value

    @property
    def combatPower(self) -> str:
        return self.__combatPower

    @combatPower.setter
    def combatPower(self, value: str) -> None:
        if value:
            self.__combatPower = value