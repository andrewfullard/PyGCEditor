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
        self.__gameObjectFilesPath: str = SomeClass.dataFolder + "gameobjectfiles.xml"
        self.__tradeRouteFilesPath: str = SomeClass.dataFolder + "traderoutefiles.xml"

       # self.__gameObjectFilesXMLRoot: Element = et.parse(self.__gameObjectFilesPath).getroot()
       #self.__tradeRouteFilesXMLRoot: Element = et.parse(self.__tradeRouteFilesPath).getroot()

    #checks if the XML root is that of a metafile by checking the first element
    #if the element tag is <File>, returns True. Otherwise False.
    def isMetaFile(self, XMLRoot) -> bool:
        if self.hasTag(XMLRoot, "File"):
            return True
        else:
            return False

    #Returns a list of XML files from a metafile such as GameObjectFiles.xml
    def parseMetaFile(self, XMLRoot) -> list():
        fileList = []
        for element in XMLRoot.iter():
            fileList.append(element.text)
        
        return fileList

    #searches GameObjectFiles for all XML files with the Planet tag.
    #returns a list of their XML roots
    def findPlanetsFiles(self, gameObjectFile) -> list():
        metaRoot = et.parse(gameObjectFile).getroot()
        if self.isMetaFile(metaRoot):
            fileList = self.parseMetaFile(metaRoot)
            planetsFiles = []

            for file in fileList:
                fileRoot = et.parse(SomeClass.dataFolder + file)
                if self.hasTag(fileRoot, "Planet"):
                    planetsFiles.append(fileRoot)
                
            return planetsFiles

        else:
            print("Not a meta file!")

    #searches TradeRouteFiles and returns a list of traderoute XML roots
    def findTradeRoutesFiles(self, tradeRoutesFile) -> list():
        metaRoot = et.parse(tradeRoutesFile).getroot()
        if self.isMetaFile(metaRoot):
            fileList = self.parseMetaFile(metaRoot)
            tradeRoutesFiles = []

            for file in fileList:
                fileRoot = et.parse(SomeClass.dataFolder + file)
                tradeRoutesFiles.append(fileRoot)
                
            return tradeRoutesFiles

         else:
            print("Not a meta file!")

    #Parses a list of XML files and returns their roots as a list
    def parseXMLFileList(self, XMLFileList) -> list():
        rootList = []
        for XMLFile in XMLFileList:
            rootList.append(et.parse(XMLFile).getroot())  
        return rootList

    #parses a comma-separated string into a Python List
    def commaSepListParser(self, entry) -> list():
        entry = entry.replace(',',' ')
        return entry.split()

    #replaces spurious commas in a Python List
    def commaReplaceInList(self, listToReplace) -> list():
        outputList = []
        for text in listToReplace:
            newText = text.replace(',','')
            outputList.append(newText)
        return outputList

    #general XML root parser to return list of element names (e.g. all planet names)
    def getNamesFromXML(self, XMLRoot) -> list():
        nameList = []

        for element in XMLRoot:
            if element.get("Name") is not None:
                nameList.append(element.get("Name"))

        return nameList

    #gets the galactic position tag value for an object of name in root XMLRoot and returns x, y
    def getStartEnd(self, name, planetList, tradeRouteRoot) -> Planet:
        for element in tradeRouteRoot.iter():
            if element.get("Name") == name:
                for child in element.iter():
                    if child.tag == "Point_A":
                        start_planet = self.getPlanet(child.text, planetList)
                    elif child.tag == "Point_B":
                        end_planet = self.getPlanet(child.text, planetList)
                    
                return start_planet, end_planet
        
        print("TradeRoute"+name+"not found!")
    
     #gets the galactic position tag value for an object of name in root XMLRoot and returns x, y
    def getLocation(self, name, XMLRoot) -> float:
        for element in XMLRoot.iter():
            if element.get("Name") == name:
                for child in element.iter("Galactic_Position"):
                    outputList = self.commaSepListParser(child.text)
                    return float(outputList[0]), float(outputList[1])
        
        print("Planet"+name+"not found!")
        
    def getPlanet(self, name, planetList) -> Planet:
        for p in planetList:
            if p.name == name:
                if p is not None:
                    return p
        
        print("Error! Planet"+name+"not found!")

     def hasTag(self, XMLRoot, XMLTag) -> bool:
        if XMLRoot.find(XMLTag) is not None:
            return True
        else:
            return False
    
    #general planet name/location search. Searches an XML root for all planet names
    #then returns a list of Planet objects with names and locations
    def getPlanetNameLocation(self, XMLRoot) -> list():
        planetList = []
        positionList = []

        for i, planetElement in enumerate(XMLRoot.iter()):
            planetName = planetElement.get("Name")
            if planetName:
                planetList.append(Planet(planetName))

                for planetChild in planetElement.iter("Galactic_Position"):
                    positionList = self.commaSepListParser(planetChild.text)
                    print(planetList, i)
                    planetList[i-1].x = float(positionList[0])
                    planetList[i-1].y = float(positionList[1])
    
        return planetList

    #parses a XML root and returns a Python list of all names in the XML tag given
    #sorts alphabetically
    def getListFromXMLRoot(self, XMLRoot, XMLTag) -> list():
        outputList = []

        for child in XMLRoot.findall(XMLTag):
            entry = self.commaReplaceInList(child.text.split())
            outputList.append(entry)

        return outputList.sort()