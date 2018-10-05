import lxml.etree as et

#incomplete example of writing XML files to disk
class XMLWriter:

    def __init__(self):
        self.__template = "campaignTemplate.xml"
        self.__templateTree = et.parse(self.__template)
        self.__templateRoot = self.__templateTree.getroot()

    def campaignWriter(self, campaign, outputName: str) -> None:
        planets = self.createListEntry(campaign.planets)
        tradeRoutes = self.createListEntry(campaign.tradeRoutes)

        self.__templateRoot.find(".//Campaign").set("Name", campaign.name)
        self.__templateRoot.find(".//Locations").text = planets
        self.__templateRoot.find(".//Trade_Routes").text = tradeRoutes

        self.__templateTree.write(outputName, xml_declaration = "1.0")

    def createListEntry(self, inputList):
        '''creates a list string to insert into a file
        requires a GameObject with the name property'''
        entry = "\n"

        for item in inputList:
            entry += (item.name + ",\n")

        return entry

    def subElementText(self, parent, subElementName, text):
        element = et.SubElement(parent, subElementName)
        element.text = text

        return element

    def writer(self, XMLRoot, outputName: str) -> None:
        XMLRoot.write(outputName, xml_declaration="1.0")