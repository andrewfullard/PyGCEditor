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

    def getCampaignNamesRoots(self, campaignRootsList) -> list:
        campaignNames = []
        campaignRoots = []

        for campaignRoot in campaignRootsList:
            campaignNames.extend(self.__xml.getNamesFromXML(campaignRoot))
            campaignRoots.extend(campaignRoot.iter("Campaign"))

        return campaignNames, campaignRoots
            
    def addPlanetsFromXML(self, planetNames, planetRoot) -> None:
        for planet in planetNames:
            newplanet = Planet(planet)
            newplanet.x, newplanet.y = self.__xml.getLocation(planet, planetRoot)
            self.repository.addPlanet(newplanet)
        
    def addTradeRoutesFromXML(self, tradeRouteNames, tradeRouteRoot) -> None:
        for route in tradeRouteNames:
            newroute = TradeRoute(route)
            newroute.start, newroute.end = self.__xml.getStartEnd(route, self.repository.planets, tradeRouteRoot)
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

        campaignFile = folder + "/XML/CampaignFiles.XML"
        planetFile = folder + "/XML/Planets.XML"
        tradeRouteFile = folder + "/XML/TradeRoutes.XML"

        xmlFileList = [planetFile, tradeRouteFile]

        rootList = self.__xml.parseXMLFileList(xmlFileList)

        planetsFromXML = self.__xml.getNamesFromXML(rootList[0])
        tradeRoutesFromXML = self.__xml.getNamesFromXML(rootList[1])

        campaignRootList = self.__xml.findMetaFileRefs(campaignFile)

        campaignNames, campaignRoots = self.getCampaignNamesRoots(campaignRootList)
       
        self.addPlanetsFromXML(planetsFromXML, rootList[0])
        self.addTradeRoutesFromXML(tradeRoutesFromXML, rootList[1])
        self.addCampaignsFromXML(campaignNames, campaignRoots)