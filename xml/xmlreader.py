import lxml.etree as et
from gameObjects.planet import Planet

''' XML with etree:

Tree.XML:

<xml? version = '1.0'?>
<root>
    <element>
        <child> </child>
    </element>

    <element.tag>
        <child.tag> child.text </child.tag>
    <element.tag>

    <element element.get = "SomeString"> </element>
    e.g. <Planet Name = "Alderaan"> </Planet>
</root>

The Tree is serialized and can be manipulated in memory.
'''

class XMLReader:

    #Probably wrong
    def __init__(self):
        self.__planetPath: str = "/Data/XML/PLANETS.XML"
        self.__tradeRoutePath: str = "Data/XML/TRADEROUTES.XML"

        self.__planetXMLRoot: Element = et.parse(self.__planetPath).getroot()
        self.__tradeXMLRoot: Element = et.parse(self.__tradeRoutePath).getroot()

    #Parses a list of XML files and returns their roots as a list
    def parseXMLFileList(self, XMLFileList):
        rootList = []
        for XMLFile in XMLFileList:
            rootList.append(et.parse(XMLFile).getroot())  
        return rootList

    #parses a comma-separated string into a Python List
    def commaSepListParser(self, entry):
        entry = entry.replace(',',' ')
        return entry.split()

    #replaces spurious commas in a Python List
    def commaReplaceInList(self, listToReplace):
        outputList = []
        for text in listToReplace:
            newText = text.replace(',','')
            outputList.append(newText)
        return outputList

    #general XML root parser to return list of element names (e.g. all planet names)
    #sorts alphabetically
    def getName(self, XMLRoot):
        nameList = []

        for element in XMLRoot.iter():
            nameList.append(element.get("Name"))
        
        return nameList.sort()

    #general planet name/location search. Searches an XML root for all planet names
    #then returns a list of Planet objects with names and locations
    def getPlanetNameLocation(self, XMLRoot):
        planetList = []
        positionList = []

        for i, planetElement in enumerate(XMLRoot.iter()):
            planetName = planetElement.get("Name")
            planetList.append(Planet(planetName))

            for planetChild in planetElement.iter("Galactic_Position"):
                positionList = self.commaSepListParser(planetChild.text)
                planetList[i].x = float(positionList[0])
                planetList[i].y = float(positionList[1])
        
        return planetList

    #parses a campaign XML root and returns a Python list of all trade route names in the campaign XML
    #sorts alphabetically
    def getCampaignTradeRouteList(self, campaignRoot):
        campaignRoutes = []

        for campaignChild in campaignRoot.findall("Trade_Routes"):
            routeEntry = self.commaReplaceInList(campaignChild.text.split())
            campaignRoutes.append(routeEntry)

        return campaignRoutes.sort()

    #REALLY SPECIFIC FUNCTIONS

    #searches the planet XML root for a planet with name planetName, and returns its x, y, z location as a list of floats
    def findPlanetLocation(self, planetName, planetXMLRoot):
        for element in planetXMLRoot.iter():
            if element.get("Name") == str(planetName):
                for child in element.iter("Galactic_Position"):
                    positionList = self.commaSepListParser(child.text)
                    return [float(i) for i in positionList]
    
    # searches the trade route XML root for a trade route with name tradeRouteName   
    # then searches for the planet locations of the start and end points
    # then returns the start and end locations, as well as the start and end planet names 
    # ALMOST CERTAINLY UNNECESSARY IN ITS CURRENT FORM           
    def findTradeRoute(self, tradeRouteName, tradeRouteXMLRoot, planetXMLRoot):
        for element in tradeRouteXMLRoot.iter():
            if element.get("Name") == str(tradeRouteName):
                #print("Found trade route", trade_route_name)
                for child in element.iter():
                    if child.tag == "Point_A":
                        start = child.text
                        startLocation = self.findPlanetLocation(start, planetXMLRoot)
                    elif child.tag == "Point_B":
                        end = child.text
                        endLocation = self.findPlanetLocation(end, planetXMLRoot)
                
                if startLocation and endLocation and (start and end):
                    return startLocation[:2], endLocation[:2], start, end
        return False, False, "", ""