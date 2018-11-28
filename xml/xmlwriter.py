import lxml.etree as et

#incomplete example of writing XML files to disk
class XMLWriter:
    '''Provides XML writing functions'''
    def __init__(self):
        self.__template = "campaignTemplate.xml"
        self.__templateTree = et.parse(self.__template)
        self.__templateRoot = self.__templateTree.getroot()

    def campaignWriter(self, campaign, outputName: str) -> None:
        '''Writes a campaign to file'''
        planets = self.createListEntry(campaign.planets)
        tradeRoutes = self.createListEntry(campaign.tradeRoutes)

        self.__templateRoot.find(".//Campaign").set("Name", campaign.name)
        self.__templateRoot.find(".//Campaign_Set").text = campaign.setName
        self.__templateRoot.find(".//Sort_Order").text = campaign.sortOrder
        self.__templateRoot.find(".//Text_ID").text = campaign.textID
        self.__templateRoot.find(".//Description_Text").text = campaign.descriptionText
        self.__templateRoot.find(".//Starting_Active_Player").text = campaign.startingActivePlayer
        self.__templateRoot.find(".//Rebel_Story_Name").text = campaign.rebelStoryName
        self.__templateRoot.find(".//Empire_Story_Name").text = campaign.empireStoryName
        self.__templateRoot.find(".//Underworld_Story_Name").text = campaign.underworldStoryName

        self.__templateRoot.find(".//Locations").text = planets
        self.__templateRoot.find(".//Trade_Routes").text = tradeRoutes

        self.writer(self.__templateTree, outputName = outputName)

    def tradeRouteWriter(self, tradeRoutes) -> None:
        '''Writes a list of trade routes to file'''
        tradeRoutesRoot = et.Element("TradeRoutes")
        tradeRoutesTree = et.ElementTree(tradeRoutesRoot)

        for t in tradeRoutes:
            route = et.SubElement(tradeRoutesRoot, "TradeRoute", Name = t.name)

            point_a = self.subElementText(route, "Point_A", t.start.name)
            point_b = self.subElementText(route, "Point_B", t.end.name)

            hsSpeedFactor = self.subElementText(route, "HS_Speed_Factor", "1.0")
            politicalControlGain = self.subElementText(route, "Political_Control_Gain", "0")
            creditGainFactor = self.subElementText(route, "Credit_Gain_Factor", "0")
            visibleLineName = self.subElementText(route, "Visible_Line_Name", "None")

        self.writer(tradeRoutesTree, outputName = "NewTradeRoutes.xml")


    def createListEntry(self, inputList):
        '''creates a list string to insert into a file
        requires a GameObject with the name property'''
        entry = "\n"

        for item in inputList:
            entry += ("\t\t\t" + item.name + ",\n")

        return entry

    def subElementText(self, parent, subElementName, text):
        '''Returns a subelement with given text'''
        element = et.SubElement(parent, subElementName)
        element.text = text

        return element

    def writer(self, XMLRoot, outputName: str) -> None:
        '''Writes XML file'''
        XMLRoot.write(outputName, xml_declaration = "1.0", pretty_print = True)