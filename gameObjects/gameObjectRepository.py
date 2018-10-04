from typing import Set

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign


class GameObjectRepository:
    '''Repository of GameObjects. Has campaigns, planets and traderoutes'''
    def __init__(self):
        self.__campaigns: Set[Campaign] = set()
        self.__planets: Set[Planet] = set()
        self.__tradeRoutes: Set[TradeRoute] = set()

    def addCampaign(self, campaign: Campaign) -> None:
        self.__campaigns.add(campaign)

    def removeCampaign(self, campaign: Campaign) -> None:
        self.__campaigns.remove(campaign)

    def addPlanet(self, planet: Planet) -> None:
        self.__planets.add(planet)

    def removePlanet(self, planet: Planet) -> None:
        self.__planets.remove(planet)

    def addTradeRoute(self, tradeRoute: TradeRoute) -> None:
        self.__tradeRoutes.add(tradeRoute)

    def removeTradeRoute(self, tradeRoute: TradeRoute) -> None:
        self.__tradeRoutes.remove(tradeRoute)

    @property
    def campaigns(self) -> Set[Campaign]:
        return set(self.__campaigns)

    @property
    def planets(self) -> Set[Planet]:
        return set(self.__planets)

    @property
    def tradeRoutes(self) -> Set[TradeRoute]:
        return set(self.__tradeRoutes)
