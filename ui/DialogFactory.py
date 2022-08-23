from gameObjects.gameObjectRepository import GameObjectRepository
from ui.qttraderoutecreator import QtTradeRouteCreator
from ui.qtcampaignproperties import QtCampaignProperties
from ui.qtautoconnectionsettings import QtAutoConnectionSettings
from gameObjects.campaign import Campaign

class DialogFactory:
    '''Produces dialog boxes'''
    def __init__(self, repository: GameObjectRepository):
        self.__repository: GameObjectRepository = repository

    def makeTradeRouteCreationDialog(self, start, end) -> QtTradeRouteCreator:
        return QtTradeRouteCreator(self.__repository, start, end)

    def makeAutoConnectionSettingsDialog(self) -> QtAutoConnectionSettings:
        return QtAutoConnectionSettings(self.__repository)
        
    def makeCampaignPropertiesDialog(self, campaign: Campaign) -> QtCampaignProperties:
        return QtCampaignProperties(campaign)
