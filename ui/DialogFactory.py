from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.campaign import Campaign
from ui.qttraderoutecreator import QtTradeRouteCreator
from ui.qtcampaignproperties import QtCampaignProperties

class DialogFactory:
    '''Produces dialog boxes'''
    def __init__(self, repository: GameObjectRepository):
        self.__repository: GameObjectRepository = repository

    def makeTradeRouteCreationDialog(self) -> QtTradeRouteCreator:
        return QtTradeRouteCreator(self.__repository)

    def makeCampaignPropertiesDialog(self, campaign: Campaign) -> QtCampaignProperties:
        return QtCampaignProperties(campaign)