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
        self.__gameObjectFilesPath: str = "/XML/gameobjectfiles.xml"
        self.__tradeRouteFilesPath: str = "/XML/traderoutefiles.xml"

        self.__gameObjectFilesXMLRoot: Element = et.parse(self.__gameObjectFilesPath).getroot()
        self.__tradeRouteFilesXMLRoot: Element = et.parse(self.__tradeRouteFilesPath).getroot()

    #checks if the XML root is that of a metafile by checking the first element
    #if the element tag is <File>, returns True. Otherwise False.
    def isMetaFile(self, XMLRoot):
        if XMLRoot[0].tag == "File":
            return True
        else
            return False

    #Returns a list of XML files from a metafile such as GameObjectFiles.xml
    def parseMetaFile(self, XMLRoot):
        fileList = []
        for element in XMLRoot.iter():
            fileList.append(element.text)
        
        return fileList

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

    #parses a XML root and returns a Python list of all names in the XML tag given
    #sorts alphabetically
    def getListFromXMLRoot(self, XMLRoot, XMLTag):
        outputList = []

        for child in XMLRoot.findall(XMLTag):
            entry = self.commaReplaceInList(child.text.split())
            outputList.append(entry)

        return outputList.sort()