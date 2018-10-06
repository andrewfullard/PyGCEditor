from typing import Set

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.aiplayer import AIPlayer

class GameObjectRepository:
    '''Repository of GameObjects. Has campaigns, planets and traderoutes'''
    def __init__(self):
        self.__campaigns: Set[Campaign] = set()
        self.__planets: Set[Planet] = set()
        self.__tradeRoutes: Set[TradeRoute] = set()

    def addCampaign(self, campaign: Campaign) -> None:
        '''Add a Campaign to the repository'''
        self.__campaigns.add(campaign)

    def removeCampaign(self, campaign: Campaign) -> None:
        '''Remove a Campaign from the repository'''
        self.__campaigns.remove(campaign)

    def addPlanet(self, planet: Planet) -> None:
        '''Add a Planet to the repository'''
        self.__planets.add(planet)

    def removePlanet(self, planet: Planet) -> None:
        '''Remove a Planet from the repository'''
        self.__planets.remove(planet)

    def addTradeRoute(self, tradeRoute: TradeRoute) -> None:
        '''Add a TradeRoute to the repository'''
        self.__tradeRoutes.add(tradeRoute)

    def removeTradeRoute(self, tradeRoute: TradeRoute) -> None:
        '''Remove a TradeRoute from the repository'''
        self.__tradeRoutes.remove(tradeRoute)

    def emptyRepository(self) -> None:
        '''Empty the repository'''
        self.__campaigns.clear()
        self.__tradeRoutes.clear()
        self.__planets.clear()

    @property
    def campaigns(self) -> Set[Campaign]:
        return set(self.__campaigns)

    @property
    def planets(self) -> Set[Planet]:
        return set(self.__planets)

    @property
    def tradeRoutes(self) -> Set[TradeRoute]:
        return set(self.__tradeRoutes)
