import lxml.etree as et
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
    def findPlanetsFiles(self, gameObjectFile) -> list():
        metaRoot = et.parse(gameObjectFile).getroot()
        if self.isMetaFile(metaRoot):
            fileList = self.parseMetaFile(metaRoot)
            planetsFiles = []

            for file in fileList:
                fileRoot = et.parse(XMLStructure.dataFolder + "/XML/" + file)
                if self.hasTag(fileRoot, "Planet"):
                    planetsFiles.append(fileRoot.getroot())
                
            return planetsFiles

        else:
            print("Not a meta file!")

    #searches a metafile and returns a list of XML roots that are referenced in the metafile
    def findMetaFileRefs(self, metaFile) -> list():
        metaRoot = et.parse(metaFile).getroot()
        if self.isMetaFile(metaRoot):
            fileList = self.parseMetaFile(metaRoot)
            metaFileRefs = []

            for file in fileList:
                fileRoot = et.parse(XMLStructure.dataFolder + "/XML/" + file)
                metaFileRefs.append(fileRoot.getroot())
                
            return metaFileRefs

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
        
        print("TradeRoute " + name + " not found!")
    
     #gets the galactic position tag value for an object of name in root XMLRoot and returns x, y
    def getLocation(self, name, XMLRoot) -> float:
        for element in XMLRoot.iter():
            if element.get("Name") == name:
                for child in element.iter("Galactic_Position"):
                    outputList = self.commaSepListParser(child.text)
                    return float(outputList[0]), float(outputList[1])
        
        print("Planet " + name + " not found!")
        
    def getPlanet(self, name, planetList) -> Planet:
        for p in planetList:
            if p.name == name:
                if p is not None:
                    return p
        
        print("Planet " + name + " not found!")

    def getTradeRoute(self, name, tradeRouteList) -> TradeRoute:
        for t in tradeRouteList:
            if t.name == name:
                if t is not None:
                    return t
        
        print("Trade Route " + name + " not found!")

    def hasTag(self, XMLRoot, XMLTag) -> bool:
        if XMLRoot.find(XMLTag) is not None:
            return True
        else:
            return False

    #parses a XML root and returns a Python list of all names in the XML tag given
    #sorts alphabetically
    def getListFromXMLRoot(self, XMLRoot, XMLTag) -> list():
        outputList = []

        for child in XMLRoot.findall(XMLTag):
            entry = self.commaReplaceInList(child.text.split())
            outputList.append(entry)

        return outputList.sort()