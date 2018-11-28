from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.aiplayer import AIPlayer
from gameObjects.unit import Unit
from gameObjects.startingForce import StartingForce
from xml.xmlreader import XMLReader
from xml.xmlstructure import XMLStructure

class RepositoryCreator:
    '''Creates a Repository of GameObjects from input XMLs'''
    def __init__(self):
        self.repository: GameObjectRepository = GameObjectRepository()
        self.__folder: str = ""
        self.__xml: XMLReader = XMLReader()

    def getNamesRootsFromXML(self, rootsList, tag: str) -> list:
        '''Takes a list of XML roots and a tag to search for
        and returns the Names and Roots of GameObjects in the list'''
        names = []
        roots = []

        for root in rootsList:
            names.extend(self.__xml.getNamesFromXML(root))
            roots.extend(root.iter(tag))

        return names, roots
            
    def addPlanetsFromXML(self, planetRoots) -> None:
        '''Takes a list of Planet GameObject XML roots and adds
        them to the repository with x and y positions'''
        for planetRoot in planetRoots:
            planetNames = self.__xml.getNamesFromXML(planetRoot)

            for name in planetNames:
                newplanet = Planet(name)
                newplanet.x, newplanet.y = self.__xml.getLocation(name, planetRoot)
                self.repository.addPlanet(newplanet)
        
    def addTradeRoutesFromXML(self, tradeRouteRoots) -> None:
        '''Takes a list of Trade Route GameObject XML roots and adds
        them to the repository with start and end planets'''
        for tradeRouteRoot in tradeRouteRoots:
            tradeRouteNames = self.__xml.getNamesFromXML(tradeRouteRoot)

            for name in tradeRouteNames:
                newroute = TradeRoute(name)
                newroute.start, newroute.end = self.__xml.getStartEnd(name, self.repository.planets, tradeRouteRoot)
                self.repository.addTradeRoute(newroute)
    
    def addFactionsFromXML(self, factionRoots) -> None:
        '''Takes a list of Faction GameObject XML roots and adds
        them to the repository'''
        for factionRoot in factionRoots:
            factionNames = self.__xml.getNamesFromXML(factionRoot)

            for name in factionNames:
                newFaction = Faction(name)
                self.repository.addFaction(newFaction)

    def addUnitsFromXML(self, unitRoots) -> None:
        '''Takes a list of unit GameObject XML roots and adds
        them to the repository'''
        dummyUnitRepository = set()
        dummyUnitRepositoryParents = []

        for unitRoot in unitRoots:
            if self.__xml.hasTag(unitRoot, ".//SpaceUnit") or self.__xml.hasTag(unitRoot, ".//Squadron") or self.__xml.hasTag(unitRoot, ".//StarBase") or\
                    self.__xml.hasTag(unitRoot, ".//GroundVehicle") or self.__xml.hasTag(unitRoot, ".//GroundInfantry") or \
                    self.__xml.hasTag(unitRoot, ".//GroundCompany") or self.__xml.hasTag(unitRoot, ".//SpecialStructure") or \
                    self.__xml.hasTag(unitRoot, ".//GenericHeroUnit") or self.__xml.hasTag(unitRoot, ".//HeroUnit") or \
                    self.__xml.hasTag(unitRoot, ".//UniqueUnit") or self.__xml.hasTag(unitRoot, ".//HeroCompany"):
                unitInfo = self.__xml.getUnitInfo(unitRoot)

                for name, power, parent, size in unitInfo:
                    newUnit = Unit(name)                    
                    newUnit.combatPower = power
                    dummyUnitRepository.add(newUnit)
                    dummyUnitRepositoryParents.append([newUnit, parent, size])
                    
        for newUnit, parent, size in dummyUnitRepositoryParents:
            if parent:
                parentUnit = self.__xml.getObject(parent, dummyUnitRepository)
                if parentUnit:
                    newUnit.combatPower = parentUnit.combatPower * size

            self.repository.addUnit(newUnit)

    def addCampaignsFromXML(self, campaignNames, campaignRoots) -> None:
        '''Takes a list of Campaign GameObject XML roots and their names, and adds
        them to the repository, after finding their planets and trade routes'''
        for (campaign, campaignRoot) in zip(campaignNames, campaignRoots):
            newCampaignPlanets = set()
            newCampaignTradeRoutes = set()
            newCampaignStartingForces = list()

            newCampaign = Campaign(campaign)
            newCampaign.setName = self.__xml.getValueFromXMLRoot(campaignRoot, ".//Campaign_Set")
            campaignPlanetNames = self.__xml.getListFromXMLRoot(campaignRoot, ".//Locations")
            campaignTradeRouteNames = self.__xml.getListFromXMLRoot(campaignRoot, ".//Trade_Routes")
            campaignStartingForces = self.__xml.getMultiTag(campaignRoot, ".//Starting_Forces")

            for p in campaignPlanetNames:
                newPlanet = self.__xml.getObject(p, self.repository.planets)
                newCampaignPlanets.add(newPlanet)

            for t in campaignTradeRouteNames:
                newRoute = self.__xml.getObject(t, self.repository.tradeRoutes)
                newCampaignTradeRoutes.add(newRoute)

            for s in campaignStartingForces:
                startingForcesEntry = self.getStartingForces(s, self.repository.planets, self.repository.units, self.repository.factions)
                newCampaignStartingForces.append(startingForcesEntry)

            newCampaign.planets = newCampaignPlanets
            newCampaign.tradeRoutes = newCampaignTradeRoutes
            newCampaign.startingForces = newCampaignStartingForces

            self.repository.addCampaign(newCampaign)

    
    def getStartingForces(self, entry: str, planetList: set, unitList: set, factionList: set) -> StartingForce:
        '''Produces a starting forces object from an XML entry'''
        entry = entry.replace(', ', ' ')
        entry = entry.split()
        factionName = entry[0]
        planetName = entry[1]
        unitName = entry[2]

        faction = self.__xml.getObject(factionName, factionList)
        planet = self.__xml.getObject(planetName, planetList)
        unit = self.__xml.getObject(unitName, unitList)

        startingForce = StartingForce(planet, faction, unit)

        return startingForce

    def constructRepository(self, folder: str) -> GameObjectRepository:
        '''Reads a mod Data folder and searches the XML metafiles within
        Creates a repository with planets, trade routes and campaigns'''
        self.__folder = folder

        XMLStructure.dataFolder = self.__folder

        gameObjectFile = self.__folder + "/XML/GameObjectFiles.XML"
        campaignFile = self.__folder + "/XML/CampaignFiles.XML"
        tradeRouteFile = self.__folder + "/XML/TradeRouteFiles.XML"
        factionFile = self.__folder + "/XML/FactionFiles.XML"

        planetRoots = self.__xml.findPlanetsFiles(gameObjectFile)
        tradeRouteRoots = self.__xml.findMetaFileRefs(tradeRouteFile)
        factionRoots = self.__xml.findMetaFileRefs(factionFile)
        unitRoots = set(self.__xml.findMetaFileRefs(gameObjectFile)) - set(planetRoots)
        
        campaignRootList = self.__xml.findMetaFileRefs(campaignFile)

        campaignNames, campaignRoots = self.getNamesRootsFromXML(campaignRootList, "Campaign")
       
        self.addPlanetsFromXML(planetRoots)
        self.addTradeRoutesFromXML(tradeRouteRoots)
        self.addFactionsFromXML(factionRoots)
        self.addUnitsFromXML(unitRoots)
        self.addCampaignsFromXML(campaignNames, campaignRoots)

        return self.repository