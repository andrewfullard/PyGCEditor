import os
import lxml.etree as et


class Config:
    """Reads external configuration file"""

    def __init__(self):
        self.__configFile = "config.xml"
        self.__configRoot = et.parse(self.__configFile).getroot()

        self.dataPath = self.__configRoot.find("DataPath").text
        self.startingForcesLibraryURL = self.__configRoot.find(
            "StartingForcesLibraryURL"
        ).text

        if not self.dataPath:
            self.dataPath = os.getcwd()

