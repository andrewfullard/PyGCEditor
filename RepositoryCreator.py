import os
import pandas as pd
from typing import List

from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.aiplayer import AIPlayer
from gameObjects.unit import Unit
from gameObjects.startingForce import StartingForce
from xmlTools.xmlreader import XMLReader
from xmlTools.xmlstructure import XMLStructure

from util import getObject


class RepositoryCreator:
    """Creates a Repository of GameObjects from input XMLs"""

    def __init__(self):
        self.repository: GameObjectRepository = GameObjectRepository()
        self.__folder: str = ""
        self.__xml: XMLReader = XMLReader()

    def getNamesRootsFromXML(self, rootsList, tag: str) -> list:
        """Takes a list of XML roots and a tag to search for
        and returns the Names and Roots of GameObjects in the list"""
        names = []
        roots = []

        for root in rootsList:
            names.extend(self.__xml.getNamesFromXML(root))
            roots.extend(root.iter(tag))

        return names, roots

    def addPlanetsFromXML(self, planetRoots) -> None:
        """Takes a list of Planet GameObject XML roots and adds
        them to the repository with x and y positions"""
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

                newplanet.starbaseLevel = int(self.__xml.getObjectProperty(name, planetRoot, ".//Max_Space_Base"))
                newplanet.spaceStructureSlots = int(self.__xml.getObjectProperty(name, planetRoot, ".//Special_Structures_Space"))
                newplanet.groundStructureSlots = int(self.__xml.getObjectProperty(name, planetRoot, ".//Special_Structures_Land"))
                self.repository.addPlanet(newplanet)

    def addTradeRoutesFromXML(self, tradeRouteRoots) -> None:
        """Takes a list of Trade Route GameObject XML roots and adds
        them to the repository with start and end planets"""
        for tradeRouteRoot in tradeRouteRoots:
            tradeRouteNames = self.__xml.getNamesFromXML(tradeRouteRoot)

            for name in tradeRouteNames:
                newroute = TradeRoute(name)
                newroute.start, newroute.end = self.__xml.getStartEnd(
                    name, self.repository.planets, tradeRouteRoot
                )
                self.repository.addTradeRoute(newroute)

    def addFactionsFromXML(self, factionRoots) -> None:
        """Takes a list of Faction GameObject XML roots and adds
        them to the repository"""
        for factionRoot in factionRoots:
            factionInfo = self.__xml.getFactionInfo(factionRoot)

            for name, color in factionInfo:
                newFaction = Faction(name)
                newFaction.color = color
                self.repository.addFaction(newFaction)

    def addUnitsFromXML(self, unitRoots) -> None:
        """Takes a list of unit GameObject XML roots and adds
        them to the repository"""

        for unitRoot in unitRoots:
            if (
                self.__xml.hasTag(unitRoot, ".//SpaceUnit")
                or self.__xml.hasTag(unitRoot, ".//Squadron")
                or self.__xml.hasTag(unitRoot, ".//StarBase")
                or self.__xml.hasTag(unitRoot, ".//GroundVehicle")
                or self.__xml.hasTag(unitRoot, ".//GroundInfantry")
                or self.__xml.hasTag(unitRoot, ".//GroundCompany")
                or self.__xml.hasTag(unitRoot, ".//SpecialStructure")
                or self.__xml.hasTag(unitRoot, ".//GenericHeroUnit")
                or self.__xml.hasTag(unitRoot, ".//HeroUnit")
                or self.__xml.hasTag(unitRoot, ".//UniqueUnit")
                or self.__xml.hasTag(unitRoot, ".//HeroCompany")
            ):
                unitInfo = self.__xml.getNamesFromXML(unitRoot)

                for name in unitInfo:
                    print("Adding unit", name)
                    newUnit = Unit(name)
                    self.repository.addUnit(newUnit)

    def addCampaignsFromXML(self, campaignNames, campaignRoots) -> None:
        """Takes a list of Campaign GameObject XML roots and their names, and adds
        them to the repository, after finding their planets and trade routes"""
        for (campaign, campaignRoot) in zip(campaignNames, campaignRoots):
            newCampaignPlanets = set()
            newCampaignTradeRoutes = set()
            newCampaignStartingForces = list()

            newCampaign = Campaign(campaign)
            newCampaign.setName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Campaign_Set"
            )
            newCampaign.sortOrder = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Sort_Order"
            )
            newCampaign.textID = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Text_ID"
            )
            newCampaign.descriptionText = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Description_Text"
            )
            newCampaign.eraStart = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Era_Start"
            )
            newCampaign.startingActivePlayer = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Starting_Active_Player"
            )
            newCampaign.rebelStoryName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Rebel_Story_Name"
            )
            newCampaign.empireStoryName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Empire_Story_Name"
            )
            newCampaign.underworldStoryName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Underworld_Story_Name"
            )

            campaignPlanetNames = self.__xml.getListFromXMLRoot(
                campaignRoot, ".//Locations"
            )
            campaignTradeRouteNames = self.__xml.getListFromXMLRoot(
                campaignRoot, ".//Trade_Routes"
            )
            campaignStartingForces = self.__xml.getMultiTag(
                campaignRoot, ".//Starting_Forces"
            )

            for p in campaignPlanetNames:
                newPlanet = getObject(p, self.repository.planets)
                newCampaignPlanets.add(newPlanet)

            for t in campaignTradeRouteNames:
                newRoute = getObject(t, self.repository.tradeRoutes)
                newCampaignTradeRoutes.add(newRoute)

            for s in campaignStartingForces:
                startingForcesEntry = self.getStartingForces(s)
                newCampaignStartingForces.append(startingForcesEntry)

            newCampaign.planets = newCampaignPlanets
            newCampaign.tradeRoutes = newCampaignTradeRoutes
            newCampaign.startingForces = pd.DataFrame(
                newCampaignStartingForces,
                columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
            )

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

    
    def getStartingForces(self, entry: str, planetList: set, unitList: set, factionList: set) -> StartingForce:
        '''Produces a starting forces object from an XML entry'''
        entry = entry.replace(', ', ' ')
        entry = entry.split()
        if len(entry) == 3:
            factionName = entry[0]
            planetName = entry[1]
            unitName = entry[2]
            return [planetName, 0, factionName, unitName, 1]
        else:
            print("Malformed starting forces entry ", entry)
            return ["Empty", 0, "Neutral", "Empty", 1]

    def getStartingForcesLibrary(self, libraryURL: str):

        startingForcesLibrary = pd.read_csv(libraryURL)

        startingForcesLibrary.drop(["ReuseEra"], inplace=True, axis=1)

        return startingForcesLibrary

    def constructRepository(
        self, folder: str, startingForcesLibraryURL: str
    ) -> GameObjectRepository:
        """Reads a mod Data folder and searches the XML metafiles within
        Creates a repository with planets, trade routes and campaigns"""
        self.__folder = folder
        self.__startingForcesLibraryURL = startingForcesLibraryURL

        XMLStructure.dataFolder = self.__folder

        gameObjectFile = self.__folder + "/XML/GameObjectFiles.XML"
        campaignFile = self.__folder + "/XML/CampaignFiles.XML"
        tradeRouteFile = self.__folder + "/XML/TradeRouteFiles.XML"
        factionFile = self.__folder + "/XML/FactionFiles.XML"

        planetRoots = self.__xml.findPlanetsFiles(gameObjectFile)
        tradeRouteRoots = self.__xml.findMetaFileRefs(tradeRouteFile)
        factionRoots = self.__xml.findMetaFileRefs(factionFile)
        
        campaignRootList = self.__xml.findMetaFileRefs(campaignFile)
        
        if os.path.exists(gameObjectFile):
            planetRoots = self.__xml.findPlanetsFiles(gameObjectFile)
            self.addPlanetsFromXML(planetRoots)
            unitRoots = set(self.__xml.findMetaFileRefs(gameObjectFile)) - set(
                planetRoots
            )
            self.addUnitsFromXML(unitRoots)

        if os.path.exists(tradeRouteFile):
            tradeRouteRoots = self.__xml.findMetaFileRefs(tradeRouteFile)
            self.addTradeRoutesFromXML(tradeRouteRoots)

        if os.path.exists(factionFile):
            factionRoots = self.__xml.findMetaFileRefs(factionFile)
            self.addFactionsFromXML(factionRoots)

        if os.path.exists(campaignFile):
            campaignRootList = self.__xml.findMetaFileRefs(campaignFile)
            campaignNames, campaignRoots = self.getNamesRootsFromXML(
                campaignRootList, "Campaign"
            )
            self.addCampaignsFromXML(campaignNames, campaignRoots)

        self.runPlanetVariantOfCheck()
        self.repository.startingForcesLibrary = self.getStartingForcesLibrary(
            self.__startingForcesLibraryURL
        )

        return self.repository
