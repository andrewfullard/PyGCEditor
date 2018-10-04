import lxml.etree as et
import os.path
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from xml.xmlstructure import XMLStructure

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

    def __init__(self):
        pass


    ''' Generic Python functions that are helpful for XML, should be moved to another class? '''

    #parses a comma-separated string into a Python List
    def commaSepListParser(self, entry: str) -> list():
        entry = entry.replace(',',' ')
        return entry.split()

    #replaces spurious commas in a Python List
    def commaReplaceInList(self, listToReplace: list) -> list():
        outputList = []
        for text in listToReplace:
            newText = text.replace(',','')
            outputList.append(newText)
        return outputList


    ''' General XML file parsing '''

    #Parses a list of XML files and returns their roots as a list
    def parseXMLFileList(self, XMLFileList: list) -> list():
        rootList = []
        for XMLFile in XMLFileList:
            rootList.append(et.parse(XMLFile).getroot())  
        return rootList

    #Checks if a given tag is present in a given XML root
    def hasTag(self, XMLRoot, XMLTag: str) -> bool:
        if XMLRoot.find(XMLTag) is not None:
            return True
        else:
            return False

    #parses a XML root and returns a Python set of all names in the XML tag given
    def getListFromXMLRoot(self, XMLRoot, XMLTag: str) -> set():
        outputSet = set()

        for child in XMLRoot.findall(XMLTag):
            entry = self.commaReplaceInList(child.text.split())
            outputSet.update(entry)

        return outputSet


    ''' Parsing EAW Meta files '''

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
        for element in XMLRoot.iter("File"):
            fileList.append(element.text)
        
        return fileList

    #searches GameObjectFiles for all XML files with the Planet tag.
    #returns a list of their XML roots
    def findPlanetsFiles(self, gameObjectFile: str) -> list():
        metaRoot = et.parse(gameObjectFile).getroot()
        if self.isMetaFile(metaRoot):
            fileList = self.parseMetaFile(metaRoot)
            planetsFiles = []

            for file in fileList:
                if not os.path.isfile(XMLStructure.dataFolder + "/XML/" + file):
                    print(file + " not found. Continuing")
                    continue

                fileRoot = et.parse(XMLStructure.dataFolder + "/XML/" + file)
                if self.hasTag(fileRoot, "Planet"):
                    planetsFiles.append(fileRoot.getroot())
                
            return planetsFiles

        else:
            print("Not a meta file! findPlanetsFiles")

    #searches a metafile and returns a list of XML roots that are referenced in the metafile
    def findMetaFileRefs(self, metaFile: str) -> list():
        metaRoot = et.parse(metaFile).getroot()
        if self.isMetaFile(metaRoot):
            fileList = self.parseMetaFile(metaRoot)
            metaFileRefs = []

            for file in fileList:
                if not os.path.isfile(XMLStructure.dataFolder + "/XML/" + file):
                    print(file + " not found. Continuing")
                    continue

                fileRoot = et.parse(XMLStructure.dataFolder + "/XML/" + file)
                metaFileRefs.append(fileRoot.getroot())
                
            return metaFileRefs

        else:
            print("Not a meta file! findMetaFileRefs")  


    ''' EAW specific XML parsing '''

    #general XML root parser to return list of element names (e.g. all planet names)
    def getNamesFromXML(self, XMLRoot) -> list():
        nameList = []

        for element in XMLRoot:
            if element.get("Name") is not None:
                nameList.append(element.get("Name"))

        return nameList

    #gets the galactic position tag value for an object of name in root XMLRoot and returns x, y
    def getStartEnd(self, name: str, planetList: set, tradeRouteRoot) -> Planet:
        for element in tradeRouteRoot.iter():
            if str(element.get("Name")).lower() == name.lower():
                for child in element.iter():
                    if child.tag == "Point_A":
                        start_planet = self.getPlanet(child.text, planetList)
                    elif child.tag == "Point_B":
                        end_planet = self.getPlanet(child.text, planetList)
                    
                return start_planet, end_planet
        
        print("TradeRoute " + name + " not found! getStartEnd")
    
    #gets the galactic position tag value for an object of name in root XMLRoot and returns x, y
    def getLocation(self, name: str, XMLRoot) -> float:
        for element in XMLRoot.iter():
            if str(element.get("Name")).lower() == name.lower():
                for child in element.iter("Galactic_Position"):
                    outputList = self.commaSepListParser(child.text)
                    return float(outputList[0]), float(outputList[1])
        
        print("Planet " + name + " not found! getLocation")

     #finds a planet object in a list of planet objects and returns it
    def getPlanet(self, name: str, planetList: set) -> Planet:
        for p in planetList:
            if p.name.lower() == name.lower():
                if p is not None:
                    return p
        
        print("Planet " + name + " not found! getPlanet")

    #finds a traderoute object in a list of traderoute objects and returns it
    def getTradeRoute(self, name: str, tradeRouteList: set) -> TradeRoute:
        for t in tradeRouteList:
            if t.name.lower() == name.lower():
                if t is not None:
                    return t
        
        print("Trade Route " + name + " not found! getTradeRoute")