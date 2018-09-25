import lxml.etree as et

#incomplete example of writing XML files to disk
class XMLWriter:

    def __init__(self):
        self.__inputTree
        self.__outputFileName

    #creates a planet list string to insert into a campaign file
    def createPlanetListEntry(self, planetList):
        entry = "\n"

        for planet in planetList:
            entry += (planet.name + ",\n")

        return entry
    
    #creates a trade route list string to insert into a campaign file
    def createTradeRouteListEntry(self, tradeRouteList):
        entry = "\n"

        for tradeRoute in tradeRouteList:
            entry += (tradeRoute.name + ",\n")
        
        return entry

    #example of creating XML from scratch. Probably better to use a template file!
    def createCampaignFile(self, campaignName = "", campaignSetName = "", campaignPlanetList = "",\
                 campaignTradeRouteList = "", sortOrderNumber = 1, textIDName = "MISSING", descriptionTextName = "MISSING"):
        root = et.Element("Campaigns")

        campaign = et.SubElement(root, "Campaign")
        campaign.attrib["Name"] = campaignName

        campaignSet = subElementText(campaign, "Campaign_Set", campaignSetName)
        sortOrder = subElementText(campaign, "Sort_Order", sortOrderNumber)

        textID = subElementText(campaign, "Text_ID", textIDName)
        descriptionText = subElementText(campaign, "Description_Text", descriptionTextName)

        cameraShiftX = subElementText(campaign, "Camera_Shift_X", 0.0)
        cameraShiftY = subElementText(campaign, "Camera_Shift_Y", 0.0)
        cameraDistance = subElementText(campaign, "Camera_Distance", 1000.0)

        locations = subElementText(campaign, "Locations", campaignPlanetList)

        tradeRoutes = subElementText(campaign, "Trade_Routes", campaignTradeRouteList)

        homeLocation = subElementText(campaign, "Home_Location", "Empire, Coruscant")

        startingActivePlayer = subElementText(campaign, "Starting_Active_Player", "Empire")

        return root

    def subElementText(self, parent, subElementName, text):
        element = et.SubElement(parent, subElementName)
        element.text = text

        return element


    def writer(self, self.__inputTree, self.__outputFileName):
        self.__inputTree.write(self.__outputFileName, xml_declaration="1.0")