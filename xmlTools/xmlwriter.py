import lxml.etree as et
from xmlTools.xmlreader import XMLReader

# incomplete example of writing XML files to disk
class XMLWriter:
    """Provides XML writing functions"""

    def __init__(self):
        self.__template = "campaignTemplate.xml"
        self.__templateTree = et.parse(self.__template)
        self.__templateRoot = self.__templateTree.getroot()

    def campaignWriter(self, campaign, outputName: str) -> None:
        """Writes a campaign to file"""
        planets = self.createListEntry(campaign.planets)
        tradeRoutes = self.createListEntry(campaign.tradeRoutes)

        campaignElement = self.__templateRoot.find(".//Campaign")

        campaignElement.set("Name", campaign.name)
        self.__templateRoot.find(".//Campaign_Set").text = campaign.setName
        self.__templateRoot.find(".//Sort_Order").text = campaign.sortOrder
        self.__templateRoot.find(".//Text_ID").text = campaign.textID
        self.__templateRoot.find(".//Description_Text").text = campaign.descriptionText
        self.__templateRoot.find(
            ".//Starting_Active_Player"
        ).text = campaign.startingActivePlayer
        self.__templateRoot.find(".//Rebel_Story_Name").text = campaign.rebelStoryName
        self.__templateRoot.find(".//Empire_Story_Name").text = campaign.empireStoryName
        self.__templateRoot.find(".//Era_Start").text = campaign.eraStart

        self.__templateRoot.find(
            ".//Underworld_Story_Name"
        ).text = campaign.underworldStoryName

        self.__templateRoot.find(".//Locations").text = planets
        self.__templateRoot.find(".//Trade_Routes").text = tradeRoutes

        for index, row in campaign.startingForces.iterrows():
            i = 0
            while i < row[4]:
                i = i + 1
                entry = str(row[2]) + " , " + str(row[0]) +" , " + str(row[3])
                for planet in campaign.planets: 
                    if planet.name.upper() == row[0]:
                        self.subElementText(
                            campaignElement, "Starting_Forces", entry, tail="\n\t\t"
                        )

        self.writer(self.__templateTree, outputName=outputName)

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
        XMLRoot.write(outputName, xml_declaration="1.0", pretty_print=True)

