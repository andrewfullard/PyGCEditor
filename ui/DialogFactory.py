from gameObjects.gameObjectRepository import GameObjectRepository
from ui.qttraderoutecreator import QtTradeRouteCreator

class DialogFactory:

    def __init__(self, repository: GameObjectRepository):
        self.__repository: GameObjectRepository = repository

    def makeTradeRouteCreationDialog(self) -> QtTradeRouteCreator:
        return QtTradeRouteCreator(self.__repository)