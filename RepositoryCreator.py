import logging
import os
import pandas as pd
from tqdm import tqdm

from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.startingForce import StartingForce
from xmlTools.xmlreader import XMLReader
from xmlTools.xmlstructure import XMLStructure

from util import getObject


logger = logging.getLogger(__name__)


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

    def addPlanetsFromXML(self, planetRoots, mapVisible: bool = True) -> None:
        """Takes a list of Planet GameObject XML roots and adds
        them to the repository with x and y positions"""
        shipyard_list = {
            "TEXT_PLANET_LIGHT": "Light Frigate",
            "TEXT_PLANET_HEAVY": "Heavy Frigate",
            "TEXT_PLANET_CAPITAL": "Capital",
            "TEXT_PLANET_DREAD": "Dreadnaught",
        }

        for planetRoot in planetRoots:
            for record in tqdm(self.__xml.getPlanetInfo(planetRoot)):
                name = record["name"]
                coordinates = record["coordinates"]

                if coordinates is None:
                    logger.warning(
                        "Planet %s not added to repository, missing coordinates", name
                    )
                    continue

                newplanet = Planet(name)
                newplanet.mapVisible = mapVisible
                newplanet.variantOf = record["variant_of"]
                newplanet.emptyXmlTags = record["empty_xml_tags"]
                newplanet.x, newplanet.y = coordinates

                # TODO better way than this hack to convert to int
                newplanet.starbaseLevel = int(float(record["starbase_level"]))
                newplanet.shipyardLevel = shipyard_list.get(
                    record["shipyard"], "No Shipyard Defined"
                )

                structure = record["structure"]
                if structure and structure.startswith("TEXT_RESOURCE_SUPPORTS_"):
                    newplanet.SupportsStructure = structure.replace(
                        "TEXT_RESOURCE_SUPPORTS_", ""
                    )
                else:
                    newplanet.SupportsStructure = "None"

                newplanet.spaceStructureSlots = int(float(record["space_slots"]))
                newplanet.groundStructureSlots = int(float(record["ground_slots"]))

                income_value = record["income"]
                if income_value:
                    newplanet.income = int(float(income_value))

                self.repository.addPlanet(newplanet)

    def addTradeRoutesFromXML(self, tradeRouteRoots) -> None:
        """Takes a list of Trade Route GameObject XML roots and adds
        them to the repository with start and end planets"""
        for tradeRouteRoot in tradeRouteRoots:
            tradeRouteNames = self.__xml.getNamesFromXML(tradeRouteRoot)

            for name in tqdm(tradeRouteNames):
                newroute = TradeRoute(name)
                try:
                    newroute.start, newroute.end = self.__xml.getStartEnd(
                        name, self.repository.planets, tradeRouteRoot
                    )
                except ValueError as err:
                    logger.warning("Skipping malformed trade route '%s': %s", name, err)
                    continue
                self.repository.addTradeRoute(newroute)

    def addFactionsFromXML(self, factionRoots) -> None:
        """Takes a list of Faction GameObject XML roots and adds
        them to the repository"""
        for factionRoot in factionRoots:
            factionInfo = self.__xml.getFactionInfo(factionRoot)

            for name, basic_ai, color, playable in factionInfo:
                newFaction = Faction(name)
                newFaction.color = color
                newFaction.aiplayer = basic_ai
                newFaction.playable = playable
                self.repository.addFaction(newFaction)

    def addCampaignsFromXML(self, campaignEntries) -> None:
        """Takes a list of (filePath, campaignName, campaignRoot) tuples and adds
        campaigns to the repository, after finding their planets and trade routes"""

        current_campaign_set = ""

        for filePath, campaign, campaignRoot in campaignEntries:
            setName = self.__xml.getValueFromXMLRoot(campaignRoot, ".//Campaign_Set")

            startingActivePlayer = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Starting_Active_Player"
            ).strip()

            logger.info("Loading campaign %s from set %s", campaign, setName)

            if setName != current_campaign_set:
                current_campaign_set = setName
                newCampaign = Campaign(campaign)
                newCampaign.fileName = filePath
            else:
                # MP campaigns don't have a starting active player
                if startingActivePlayer:
                    self.repository.getCampaignBySetName(setName).playableFactions.add(
                        self.repository.getFactionByName(startingActivePlayer)
                    )
                continue

            newCampaign.setName = setName
            if startingActivePlayer:
                newCampaign.playableFactions.add(
                    self.repository.getFactionByName(startingActivePlayer)
                )

            newCampaignPlanets = set()
            newCampaignTradeRoutes = set()
            newCampaignStartingForces = list()

            campaignPlanetNames = self.__xml.getListFromXMLRoot(
                campaignRoot, ".//Locations"
            )

            new_campaign_locations = campaignPlanetNames

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
            useDefaultForcesText = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Use_Default_Forces"
            )

            newCampaign.useDefaultForces = self.__xml.stringToBool(useDefaultForcesText)

            newCampaign.rebelStoryName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Rebel_Story_Name"
            )
            newCampaign.empireStoryName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Empire_Story_Name"
            )
            newCampaign.underworldStoryName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Underworld_Story_Name"
            )

            newCampaign.storyName = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Story_Name"
            )

            newCampaign.isListed = self.__xml.getValueFromXMLRoot(
                campaignRoot, ".//Is_Listed"
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
            # TODO sum up identical entries into the Amount column
            newCampaign.startingForces = pd.DataFrame(
                newCampaignStartingForces,
                columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
            )

            logger.info(
                "Found %d planets and %d trade routes",
                len(newCampaignPlanets),
                len(newCampaignTradeRoutes),
            )

            self.repository.addCampaign(newCampaign)

    def runPlanetVariantOfCheck(self) -> None:
        for planet in tqdm(self.repository.planets):
            if (planet.x is None) or (planet.y is None):
                logger.warning("%s needs parent coordinates", planet.name)
                if planet.variantOf != "":
                    parent = self.getPlanetParentWithCoordinates(planet)
                    planet.x = parent.x
                    planet.y = parent.y
                    logger.info(
                        "%s now uses %s coordinates!%s, %s",
                        planet.name,
                        parent.name,
                        parent.x,
                        parent.y,
                    )

                else:
                    logger.error("%s has no parent!", planet.name)

    def getPlanetParentWithCoordinates(self, planet) -> Planet:
        p = self.repository.getPlanetByName(planet.variantOf)
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

    def getStartingForces(self, entry: str) -> StartingForce:
        """Produces a starting forces object from an XML entry"""
        entry = entry.replace(",", " ")
        entry = entry.split()
        if len(entry) == 3:
            factionName = entry[0]
            planetName = entry[1]
            unitName = entry[2]
            return [planetName, 0, factionName, unitName, 1]
        else:
            logger.warning("Malformed starting forces entry %s", entry)
            return ["Empty", 0, "Neutral", "Empty", 1]

    def getStartingForcesLibrary(self, libraryURL: str):
        if not libraryURL or not os.path.isfile(libraryURL):
            logger.warning("Starting forces library not found; continuing without it")
            return None

        try:
            startingForcesLibrary = pd.read_csv(libraryURL)
        except (
            FileNotFoundError,
            OSError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            UnicodeDecodeError,
        ) as err:
            logger.error("Failed to load starting forces library '%s': %s", libraryURL, err)
            return None

        required_columns = {
            "Planet",
            "Era",
            "Owner",
            "ObjectType",
            "Amount",
            "ReuseEra",
        }
        missing_columns = required_columns.difference(startingForcesLibrary.columns)
        if missing_columns:
            logger.error(
                "Starting forces library is malformed; missing columns: %s",
                ", ".join(sorted(missing_columns)),
            )
            return None

        current_planet = None
        current_era = 0

        try:
            for index, row in tqdm(startingForcesLibrary.iterrows()):
                if row["Planet"] != current_planet:
                    current_planet = row["Planet"]

                if row["Era"] != current_era:
                    current_era = row["Era"]
                    if not pd.isna(row["ReuseEra"]):
                        era_to_reuse = row["ReuseEra"]
                        reuse_filter = (startingForcesLibrary.Era == era_to_reuse) & (
                            startingForcesLibrary.Planet == current_planet
                        )
                        data_to_add = startingForcesLibrary[reuse_filter].copy()
                        data_to_add = data_to_add.assign(Era=current_era)
                        startingForcesLibrary = pd.concat(
                            [startingForcesLibrary, data_to_add]
                        )
                        continue

            startingForcesLibrary.reset_index(drop=True, inplace=True)

            startingForcesLibrary.drop(["ReuseEra"], inplace=True, axis=1)
            startingForcesLibrary.dropna(inplace=True)

            startingForcesLibrary.sort_values(by=["Planet"], inplace=True)
        except (KeyError, TypeError, ValueError) as err:
            logger.error(
                "Starting forces library is malformed; continuing without it: %s", err
            )
            return None

        return startingForcesLibrary

    def constructRepository(
        self, dataFolders, startingForcesLibraryURL: str
    ) -> GameObjectRepository:
        """Reads one or more mod Data folders and searches the XML metafiles within.
        dataFolders is an ordered list [base, submod1, submod2, ...] where later entries
        have higher priority and override earlier ones.
        Creates a repository with planets, trade routes and campaigns"""
        if isinstance(dataFolders, str):
            dataFolders = [dataFolders]

        self.__folder = dataFolders[0]
        self.__startingForcesLibraryURL = startingForcesLibraryURL

        XMLStructure.dataFolder = dataFolders[0]
        XMLStructure.dataFolders = dataFolders
        # Derive submod names from folders beyond the base: ModPath/SubmodName/Data
        XMLStructure.submods = [
            os.path.basename(os.path.dirname(f)) for f in dataFolders[1:]
        ]

        gameObjectFile = dataFolders[0] + "/XML/GameObjectFiles.XML"
        campaignFile = dataFolders[0] + "/XML/CampaignFiles.XML"
        tradeRouteFile = dataFolders[0] + "/XML/TradeRouteFiles.XML"
        factionFile = dataFolders[0] + "/XML/FactionFiles.XML"

        def metaFileExists(name):
            return any(
                os.path.exists(os.path.join(f, "XML", name)) for f in dataFolders
            )

        if metaFileExists("GameObjectFiles.XML"):
            logger.info("Loading Planets")
            planetRoots = self.__xml.findPlanetsFiles(
                gameObjectFile, dataFolders, excludedFiles={"Planets_Dummy.xml"}
            )
            self.addPlanetsFromXML(planetRoots)
            dummyPlanetRoots = self.__xml.findPlanetFileByName(
                "Planets_Dummy.xml", dataFolders
            )
            self.addPlanetsFromXML(dummyPlanetRoots, mapVisible=False)

        if metaFileExists("TradeRouteFiles.XML"):
            logger.info("Loading Trade Routes")
            tradeRouteRoots = self.__xml.findMetaFileRefs(tradeRouteFile, dataFolders)
            self.addTradeRoutesFromXML(tradeRouteRoots)

        if metaFileExists("FactionFiles.XML"):
            logger.info("Loading Factions")
            factionRoots = self.__xml.findMetaFileRefs(factionFile, dataFolders)
            self.addFactionsFromXML(factionRoots)

        if metaFileExists("CampaignFiles.XML"):
            logger.info("Loading Campigns")
            campaignPathRootList = self.__xml.findMetaFileRefsWithPaths(
                campaignFile, dataFolders
            )
            campaignEntries = [
                (filePath, name, root)
                for filePath, fileRoot in campaignPathRootList
                for name, root in zip(
                    self.__xml.getNamesFromXML(fileRoot), fileRoot.iter("Campaign")
                )
            ]
            self.addCampaignsFromXML(campaignEntries)

        logger.info("Checking for planet variants")
        self.runPlanetVariantOfCheck()
        logger.info("Loading starting forces")
        self.repository.startingForcesLibrary = self.getStartingForcesLibrary(
            self.__startingForcesLibraryURL
        )

        return self.repository
