from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.aiplayer import AIPlayer
from xmlUtil.xmlreader import XMLReader
from xmlUtil.xmlstructure import XMLStructure

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
                newplanet.variantOf = self.__xml.getVariantOfValue(name, planetRoot)
                coordinates = self.__xml.getLocation(name, planetRoot)
                if coordinates == None:
                    newplanet.x, newplanet.y = None, None
                else:
                    newplanet.x, newplanet.y = coordinates

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
                newfaction = Faction(name)
                self.repository.addFaction(newfaction)

    def addCampaignsFromXML(self, campaignNames, campaignRoots) -> None:
        '''Takes a list of Campaign GameObject XML roots and their names, and adds
        them to the repository, after finding their planets and trade routes'''
        for (campaign, campaignRoot) in zip(campaignNames, campaignRoots):
            newCampaignPlanets = set()
            newCampaignTradeRoutes = set()

            newCampaign = Campaign(campaign)
            newCampaign.setName = self.__xml.getValueFromXMLRoot(campaignRoot, ".//Campaign_Set")
            campaignPlanetNames = self.__xml.getListFromXMLRoot(campaignRoot, ".//Locations")
            campaignTradeRouteNames = self.__xml.getListFromXMLRoot(campaignRoot, ".//Trade_Routes")

            for p in campaignPlanetNames:
                newPlanet = self.__xml.getPlanet(p, self.repository.planets)
                newCampaignPlanets.add(newPlanet)

            for t in campaignTradeRouteNames:
                newRoute = self.__xml.getPlanet(t, self.repository.tradeRoutes)
                newCampaignTradeRoutes.add(newRoute)

            newCampaign.planets = newCampaignPlanets
            newCampaign.tradeRoutes = newCampaignTradeRoutes

            self.repository.addCampaign(newCampaign)

    def runPlanetVariantOfCheck(self) -> None:
        for planet in self.repository.planets:
            if (planet.x is None) or (planet.y is None):
                print(planet.name + " needs parent coordinates")
                if planet.variantOf != "":
                    parent = self.getPlanetParentWithCoordinates(planet)
                    planet.x = parent.x
                    planet.y = parent.y
                    print(planet.name + " now uses " + parent.name + " coordinates!" + parent.x.__str__() + ", " + parent.y.__str__())

                else:
                    print(planet.name + " has no parent!")



    def getPlanetParentWithCoordinates(self, planet) -> Planet:
        p =  self.repository.getPlanetByName(planet.variantOf)
        if p is not None:
            if (p.x is None) & (p.y is None):
                if p.variantOf == "":
                    return None
                else:
                    return self.getPlanetParentWithCoordinates(p)
            else:
                return p
        else:
            return None



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
        
        campaignRootList = self.__xml.findMetaFileRefs(campaignFile)

        campaignNames, campaignRoots = self.getNamesRootsFromXML(campaignRootList, "Campaign")
       
        self.addPlanetsFromXML(planetRoots)
        self.addTradeRoutesFromXML(tradeRouteRoots)
        self.addFactionsFromXML(factionRoots)
        self.addCampaignsFromXML(campaignNames, campaignRoots)
        self.runPlanetVariantOfCheck()
        return self.repository