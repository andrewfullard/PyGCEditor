import lxml.etree as et
from xmlTools.xmlreader import XMLReader

# incomplete example of writing XML files to disk
class XMLWriter:
    """Provides XML writing functions"""

    def __init__(self):
        self.__root_name = "Campaigns"
        self.root = None

    def campaignWriter(self, campaign, outputName: str) -> None:
        """Writes a campaign to file"""

        planets = self.createListEntry(campaign.planets)
        tradeRoutes = self.createListEntry(campaign.tradeRoutes)

        self.root = et.Element(self.__root_name)

        era_limiter = campaign.startingForces.Era == int(campaign.eraStart)

        filtered_starting_forces = campaign.startingForces[era_limiter]

        for playableFaction in campaign.playableFactions:
            campaignElement = et.SubElement(self.root, "Campaign")

            campaignElement.set("Name", campaign.name + "_" + playableFaction.name)
            self.subElementText(campaignElement, "Campaign_Set", campaign.setName)
            self.subElementText(campaignElement, "Sort_Order", campaign.sortOrder)
            self.subElementText(campaignElement, "Is_Listed", "False")

            self.subElementText(campaignElement, "Supports_Custom_Settings", "False")
            self.subElementText(campaignElement, "Show_Completed_Tab", "True")

            self.subElementText(campaignElement, "Text_ID", campaign.textID)
            self.subElementText(campaignElement, "Description_Text", campaign.descriptionText)

            self.subElementText(campaignElement, "Camera_Shift_X", "0.0")
            self.subElementText(campaignElement, "Camera_Shift_Y", "0.0")
            self.subElementText(campaignElement, "Camera_Distance", "1000.0")

            self.subElementText(campaignElement, "Locations", planets)
            self.subElementText(campaignElement, "Trade_Routes", tradeRoutes)

            self.subElementText(campaignElement, "Starting_Active_Player", playableFaction.name)

            for faction in campaign.playableFactions:
                if faction.name is not playableFaction.name:
                    # Right now the players don't import properly
                    self.subElementText(campaignElement, "AI_Player_Control", faction.name +", None")
                else: 
                    self.subElementText(campaignElement, "AI_Player_Control", faction.name +", SandboxHuman")

            for faction in campaign.playableFactions:
                self.subElementText(campaignElement, "Markup_Filename", faction.name +", DefaultGalacticHints")

            self.subElementText(campaignElement, "Human_Victory_Conditions", "Galactic_All_Planets_Controlled")
            self.subElementText(campaignElement, "AI_Victory_Conditions", "Galactic_All_Planets_Controlled")

            self.subElementText(campaignElement, "Story_Name", "Rebel, Conquests\Progressive\Story_Plots_Sandbox_FullProgressive_Rebel.xml,\nEmpire, Conquests\Progressive\Story_Plots_Sandbox_FullProgressive_Empire.xml,\nUnderworld, Conquests\Progressive\Story_Plots_Sandbox_FullProgressive_Container.xml,\nEmpireoftheHand, Conquests\Story_Plots_Generic_EmpireoftheHand.xml,\nTeradoc, Conquests\Story_Plots_Generic_Teradoc.xml,\nPirates, Conquests\Story_Plots_Generic_Pirates.xml,\nCorporate_Sector, Conquests\Story_Plots_Generic_Corporate_Sector.xml,\nHutts, Conquests\Story_Plots_Generic_Hutts.xml,\nHapes_Consortium, Conquests\Story_Plots_Generic_Hapes_Consortium.xml,\nPentastar, Conquests\Story_Plots_Generic_Pentastar.xml")

            for faction in campaign.playableFactions:
                self.subElementText(campaignElement, "Starting_Credits", faction.name +", 10000")
                self.subElementText(campaignElement, "Starting_Tech_Level", faction.name +", 1")
                self.subElementText(campaignElement, "Max_Tech_Level", faction.name +", 5")

            for index, row in filtered_starting_forces.iterrows():
                i = 0
                while i < row.Amount:
                    i = i + 1
                    entry = str(row.Owner) + ", " + str(row.Planet) +", " + str(row.ObjectType)
                    for planet in campaign.planets:
                        if planet.name.upper() == row.Planet.upper():
                            self.subElementText(
                                campaignElement, "Starting_Forces", entry
                            )
        tree = et.ElementTree(self.root)
        self.writer(tree, outputName=campaign.name + ".XML")

    def tradeRouteWriter(self, tradeRoutes) -> None:
        """Writes a list of trade routes to file"""
        tradeRoutesRoot = et.Element("TradeRoutes")
        tradeRoutesTree = et.ElementTree(tradeRoutesRoot)

        for t in tradeRoutes:
            route = et.SubElement(tradeRoutesRoot, "TradeRoute", Name=t.name)

            point_a = self.subElementText(route, "Point_A", t.start.name)
            point_b = self.subElementText(route, "Point_B", t.end.name)

            hsSpeedFactor = self.subElementText(route, "HS_Speed_Factor", "1.0")
            politicalControlGain = self.subElementText(
                route, "Political_Control_Gain", "0"
            )
            creditGainFactor = self.subElementText(route, "Credit_Gain_Factor", "0")
            visibleLineName = self.subElementText(route, "Visible_Line_Name", "DEFAULT")

        self.writer(tradeRoutesTree, outputName="NewTradeRoutes.xml")

    def planetCoordinatesWriter(self, path, planetFilesRoots, newPlanetData):
        """Save updated planet coordinates"""
        for file, root in planetFilesRoots.items():
            for element in root.iter("Planet"):
                name = str(element.get("Name"))
                try:
                    newData = newPlanetData[name]
                    for child in element.iter("Galactic_Position"):
                        outputList = XMLReader().commaSepListParser(child.text)
                        pos_text = (
                            str(newData[0])
                            + ", "
                            + str(newData[1])
                            + ", "
                            + str(outputList[2])
                        )
                        child.text = pos_text
                        break
                except (KeyError):
                    pass
            root.write(path + file, xml_declaration="1.0", pretty_print=True)

    def createListEntry(self, inputList):
        """creates a list string to insert into a file
        requires a GameObject with the name property"""
        entry = "\n"
        inputList = sorted(inputList, key=lambda entry: entry.name)
        for item in inputList:
            entry += "\t\t\t" + item.name + ",\n"

        return entry

    def subElementText(self, parent, subElementName, text, tail=""):
        """Returns a subelement with given text"""
        element = et.SubElement(parent, subElementName)
        element.text = text
        if tail:
            element.tail = tail

        return element

    def writer(self, XMLRoot, outputName: str) -> None:
        """Writes XML file"""
        XMLRoot.write(outputName, xml_declaration="1.0", pretty_print=True, encoding="utf-8")

