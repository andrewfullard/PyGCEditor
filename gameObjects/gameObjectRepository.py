from typing import List, Set

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.aiplayer import AIPlayer
from gameObjects.unit import Unit

class GameObjectRepository:
    '''Repository of GameObjects. Has campaigns, planets and traderoutes'''
    def __init__(self):
        self.__campaigns: Set[Campaign] = set()
        self.__planets: Set[Planet] = set()
        self.__tradeRoutes: Set[TradeRoute] = set()
        self.__factions: Set[Faction] = set()
        self.__aiplayers: Set[AIPlayer] = set()
        self.__units: Set[Unit] = set()

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

    def planetExists(self, name: str) -> None:
        '''Returns true if a planet exists by name, false otherwise'''
        try:
            self.getPlanetByName(name)
            return True
        except:
            return False

    def tradeRouteExists(self, startName: str, endName: str) -> None:
        '''Returns true if a planet exists by name, false otherwise'''
        try:
            self.getTradeRouteByPlanets(self.getPlanetByName(startName), self.getPlanetByName(endName))
            return True
        except:
            return False

    def getPlanetByName(self, name: str) -> None:
        '''Returns a planet object given its name'''
        for planet in self.planets:
            if planet.name == name:
                return planet

        raise RuntimeError("Searching for non existing planet " + name)

    def getTradeRouteByPlanets(self, start: Planet, end: Planet) -> None:
        '''Returns a traderoute object given its start and end planets'''
        for tradeRoute in self.tradeRoutes:
            if (tradeRoute.start == start) and (tradeRoute.end == end):
                return tradeRoute

        raise RuntimeError("Searching for non existing Trade Route")

    def getPlanetNames(self) -> List[str]:
        '''Returns a list containing all Planet names'''
        return [x.name for x in self.__planets]

    def addTradeRoute(self, tradeRoute: TradeRoute) -> None:
        '''Add a TradeRoute to the repository'''
        self.__tradeRoutes.add(tradeRoute)

    def removeTradeRoute(self, tradeRoute: TradeRoute) -> None:
        '''Remove a TradeRoute from the repository'''
        self.__tradeRoutes.remove(tradeRoute)

    def addFaction(self, faction: Faction) -> None:
        '''Add a Faction to the repository'''
        self.__factions.add(faction)

    def removeFaction(self, faction: Faction) -> None:
        '''Remove a Faction from the repository'''
        self.__factions.remove(faction)

    def addAIPlayer(self, aiplayer: AIPlayer) -> None:
        '''Add an AI Player to the repository'''
        self.__aiplayers.add(aiplayer)

    def removeAIPlayer(self, aiplayer: AIPlayer) -> None:
        '''Remove an AI Player from the repository'''
        self.__aiplayers.remove(aiplayer)

    def addUnit(self, unit: Unit) -> None:
        '''Add a unit to the repository'''
        self.__units.add(unit)

    def removeUnit(self, unit: Unit) -> None:
        '''Remove a unit from the repository'''
        self.__units.remove(unit)

    def emptyRepository(self) -> None:
        '''Empty the repository'''
        self.__campaigns.clear()
        self.__tradeRoutes.clear()
        self.__planets.clear()
        self.__factions.clear()
        self.__aiplayers.clear()
        self.__units.clear()

    @property
    def campaigns(self) -> Set[Campaign]:
        return set(self.__campaigns)

    @property
    def planets(self) -> Set[Planet]:
        return set(self.__planets)

    @property
    def tradeRoutes(self) -> Set[TradeRoute]:
        return set(self.__tradeRoutes)

    @property
    def factions(self) -> Set[Faction]:
        return set(self.__factions)

    @property
    def aiplayers(self) -> Set[AIPlayer]:
        return set(self.__aiplayers)

    @property
    def units(self) -> Set[Unit]:
        return set(self.__units)

