import lxml.etree as et
import os.path
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.startingForce import StartingForce
from xmlTools.xmlstructure import XMLStructure

""" XML with etree:

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
"""


class XMLReader:
    """Provides XML read functions"""

    def __init__(self):
        pass

    """ Generic Python functions that are helpful for XML, should be moved to another class? """

    def commaSepListParser(self, entry: str) -> list():
        """Parses a comma-separated string into a Python List"""
        entry = entry.replace(",", " ")
        return entry.split()

    def commaReplaceInList(self, listToReplace: list) -> list():
        """Replaces spurious commas in a Python List"""
        outputList = []
        for text in listToReplace:
            newText = text.replace(",", "")
            outputList.append(newText)
        return outputList

    """ General XML file parsing """

    def parseXMLFileList(self, XMLFileList: list) -> list():
        """Parses a list of XML files and returns their roots as a list"""
        rootList = []
        for XMLFile in XMLFileList:
            rootList.append(et.parse(XMLFile).getroot())
        return rootList

    def hasTag(self, XMLRoot, XMLTag: str) -> bool:
        """Checks if a given tag is present in a given XML root"""
        if XMLRoot.find(XMLTag) is not None:
            return True
        else:
            return False

    def getValueFromXMLRoot(self, XMLRoot, XMLTag: str) -> str():
        """Returns the text from a given tag name in the given root"""
        if XMLRoot.find(XMLTag) is not None:
            return XMLRoot.find(XMLTag).text
        else:
            print("Tag ", XMLTag, " not found")
            return ""

    def getListFromXMLRoot(self, XMLRoot, XMLTag: str) -> set():
        """Parses a XML root and returns a Python set of all names in the XML tag given"""
        outputSet = set()

        et.strip_tags(XMLRoot, et.Comment)

        for child in XMLRoot.findall(XMLTag):
            entry = self.commaReplaceInList(child.text.split())
            outputSet.update(entry)

        return outputSet

    """ Parsing EAW Meta files """

    def isMetaFile(self, XMLRoot) -> bool:
        """Checks if the XML root is that of a metafile by checking the first element.
            If the element tag is <File>, returns True. Otherwise False."""
        if self.hasTag(XMLRoot, "File"):
            return True
        else:
            return False

    def parseMetaFile(self, XMLRoot) -> list():
        """Returns a list of XML files from a metafile such as GameObjectFiles.xml"""
        fileList = []
        for element in XMLRoot.iter("File"):
            fileList.append(element.text)

        return fileList

    def findPlanetsFiles(self, gameObjectFile: str) -> list():
        """Searches GameObjectFiles for all XML files with the Planet tag.
            Returns a list of their XML roots"""
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

    def findPlanetFilesAndRoots(self, gameObjectFile: str) -> list():
        """Searches GameObjectFiles for all XML files with the Planet tag.
            Returns a dictionary of file names and their XML roots"""
        metaRoot = et.parse(gameObjectFile).getroot()
        if self.isMetaFile(metaRoot):
            fileList = self.parseMetaFile(metaRoot)
            planetsFiles = {}

            for file in fileList:
                if not os.path.isfile(XMLStructure.dataFolder + "/XML/" + file):
                    print(file + " not found. Continuing")
                    continue

                fileRoot = et.parse(XMLStructure.dataFolder + "/XML/" + file)
                if self.hasTag(fileRoot, "Planet"):
                    planetsFiles[file] = fileRoot

            return planetsFiles

        else:
            print("Not a meta file! findPlanetsFiles")

    def findMetaFileRefs(self, metaFile: str) -> list():
        """Searches a metafile and returns a list of XML roots that are referenced in the metafile"""
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

    """ EAW specific XML parsing """

    def getNamesFromXML(self, XMLRoot) -> list():
        """General XML root parser to return list of element Names (e.g. all planet names)"""
        nameList = []

        for element in XMLRoot:
            if element.get("Name") is not None:
                nameList.append(element.get("Name"))

        return nameList

    def getFactionInfo(self, XMLRoot) -> list():
        """XML root parser to return list of faction name and color (color in 0-1 RGBA space)"""
        factionList = []

        for element in XMLRoot:
            if element.get("Name") is not None:
                colorElement = element.find("Color")
                color = [float(x.strip()) / 255 for x in colorElement.text.split(",")]
                factionList.append([element.get("Name"), color])

        return factionList

    def getUnitInfo(self, XMLRoot) -> list():
        """XML root parser to return list of unit name, parent, combat power, and company size"""
        namePowerList = []

        # Loop through root
        for element in XMLRoot:
            # We found a named object
            if element.get("Name") is not None:
                # Is it a variant? Grab the parent if so
                parentElement = element.find("Variant_Of_Existing_Type")
                if parentElement is not None:
                    parent = parentElement.text.strip()
                else:
                    parent = False

                companySize = 0

                # Check for a ground company or squadron
                companyElements = element.findall("Company_Units")
                squadronElements = element.findall("Squadron_Units")

                if companyElements:
                    for companyElement in companyElements:
                        companySize += len(companyElement.text.split())
                        parent = [x.strip() for x in companyElement.text.split(",")][0]
                elif squadronElements:
                    for squadronElement in squadronElements:
                        companySize += len(squadronElement.text.split())
                        parent = [x.strip() for x in squadronElement.text.split(",")][0]
                else:
                    companySize = 1

                # Get combat power if available
                powerElement = element.find("AI_Combat_Power")
                if powerElement is not None:
                    power = float(powerElement.text)
                    namePowerList.append(
                        [element.get("Name"), power, False, companySize]
                    )
                else:
                    namePowerList.append([element.get("Name"), 0, parent, companySize])

        return namePowerList

    def getStartEnd(self, name: str, planetList: set, tradeRouteRoot) -> Planet:
        """Gets the start and end Planet objects for a trade route of name in root tradeRouteRoot and returns start, end"""
        for element in tradeRouteRoot.iter():
            if str(element.get("Name")).lower() == name.lower():
                start_planet = self.getObject(element.find("Point_A").text, planetList)
                end_planet = self.getObject(element.find("Point_B").text, planetList)

                return start_planet, end_planet

        print("TradeRoute " + name + " not found! getStartEnd")

    def getLocation(self, name: str, XMLRoot) -> float:
        """Gets the galactic position tag value for an object of name in root XMLRoot and returns x, y"""
        for element in XMLRoot.iter():
            if str(element.get("Name")).lower() == name.lower():
                for child in element.iter("Galactic_Position"):
                    outputList = self.commaSepListParser(child.text)
                    return float(outputList[0]), float(outputList[1])

        print("Planet " + name + " not found! getLocation")

    def getObjectProperty(self, name: str, XMLRoot, tag: str) -> str:
        """Gets the text from a given tag, for a given object, in a given XML file root"""
        for element in XMLRoot.iter():
            if str(element.get("Name")).lower() == name.lower():
                tagFind = element.find(tag)
                if tagFind is not None:
                    return tagFind.text
                else:
                    return "0"

        print("Object " + name + " not found!")

    def getObject(self, name: str, objectList: set):
        """Finds a named object in a list of objects and returns it"""
        for o in objectList:
            if o.name.lower() == name.lower():
                if o is not None:
                    return o

        print("Object " + name + " not found!")

    def getMultiTag(self, XMLRoot, tagName: str) -> list():
        """Returns a list of text from multiple of the same tag"""
        result = []
        for child in XMLRoot.findall(tagName):
            result.append(child.text)

        return result
