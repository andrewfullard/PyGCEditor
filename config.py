import os
import lxml.etree as et


class Config:
    """Reads external configuration file"""

    def __init__(self):
        self.__configFile = "config.xml"
        self.__configRoot = et.parse(self.__configFile).getroot()

        self.autoPlanetConnectionDistance = int(self.__configRoot.find("MaximumFleetMovementDistance").text)
        self.startingForcesLibraryURL = self.__configRoot.find(
            "StartingForcesLibraryURL"
        ).text

        mod_path_el = self.__configRoot.find("ModPath")

        if mod_path_el is not None:
            self.modPath = mod_path_el.text.strip()
            # Submod names in ascending priority order (last = highest priority)
            self.submods = [e.text.strip() for e in self.__configRoot.findall("Submod")]
            self.dataFolders = [os.path.join(self.modPath, "Data")]
            for submod in self.submods:
                self.dataFolders.append(os.path.join(self.modPath, submod, "Data"))
        else:
            self.modPath = os.getcwd()
            self.submods = []
            self.dataFolders = [os.path.join(self.modPath, "Data")]

        # dataPath remains the base Data folder for backward compatibility
        self.dataPath = self.dataFolders[0]

