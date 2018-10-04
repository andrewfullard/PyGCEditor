from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from xml.xmlreader import XMLReader
from xml.xmlstructure import XMLStructure

class RepositoryCreator:
    def __init__(self):
        self.repository: GameObjectRepository = GameObjectRepository()
        
        self.__xml: XMLReader = XMLReader()

    def getNamesRootsFromXML(self, rootsList, tag) -> list:
        names = []
        roots = []

        for root in rootsList:
            names.extend(self.__xml.getNamesFromXML(root))
            roots.extend(root.iter(tag))

        return names, roots
            
    def addPlanetsFromXML(self, planetRoots) -> None:
        for planetRoot in planetRoots:
            planetNames = self.__xml.getNamesFromXML(planetRoot)

            for name in planetNames:
                newplanet = Planet(name)
                newplanet.x, newplanet.y = self.__xml.getLocation(name, planetRoot)
                self.repository.addPlanet(newplanet)
        
    def addTradeRoutesFromXML(self, tradeRouteRoots) -> None:
        for tradeRouteRoot in tradeRouteRoots:
            tradeRouteNames = self.__xml.getNamesFromXML(tradeRouteRoot)

            for name in tradeRouteNames:
                newroute = TradeRoute(name)
                newroute.start, newroute.end = self.__xml.getStartEnd(name, self.repository.planets, tradeRouteRoot)
                self.repository.addTradeRoute(newroute)

    def addCampaignsFromXML(self, campaignNames, campaignRoots) -> None:
        for (campaign, campaignRoot) in zip(campaignNames, campaignRoots):
            newCampaignPlanets = set()
            newCampaignTradeRoutes = set()

            newCampaign = Campaign(campaign)
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

    def constructRepository(self, folder: str) -> None:
        XMLStructure.dataFolder = folder

        gameObjectFile = folder + "/XML/GameObjectFiles.XML"
        campaignFile = folder + "/XML/CampaignFiles.XML"
        tradeRouteFile = folder + "/XML/TradeRouteFiles.XML"

        planetRoots = self.__xml.findPlanetsFiles(gameObjectFile)
        tradeRouteRoots = self.__xml.findMetaFileRefs(tradeRouteFile)

        print(planetRoots)

        campaignRootList = self.__xml.findMetaFileRefs(campaignFile)

        campaignNames, campaignRoots = self.getNamesRootsFromXML(campaignRootList, "Campaign")
       
        self.addPlanetsFromXML(planetRoots)
        self.addTradeRoutesFromXML(tradeRouteRoots)
        self.addCampaignsFromXML(campaignNames, campaignRoots)