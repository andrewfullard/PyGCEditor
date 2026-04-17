import os
import lxml.etree as et


class Config:
    """Reads external configuration file"""

    def __init__(self):
        self.__configFile = "config.xml"
        self.__configTree = et.parse(self.__configFile)
        self.__configRoot = self.__configTree.getroot()
        self.__loadValuesFromConfig()

    def save(
        self,
        modPath: str,
        submods: list,
        autoPlanetConnectionDistance: int,
        startingForcesLibraryURL: str,
    ) -> None:
        """Persist config values to config.xml and refresh in-memory values."""
        self.__setElementText("ModPath", modPath)
        self.__setElementText(
            "MaximumFleetMovementDistance", str(autoPlanetConnectionDistance)
        )
        self.__setElementText("StartingForcesLibraryURL", startingForcesLibraryURL)

        for el in self.__configRoot.findall("Submod"):
            self.__configRoot.remove(el)

        for submod in submods:
            submodName = str(submod).strip()
            if submodName:
                submodElement = et.Element("Submod")
                submodElement.text = submodName
                self.__configRoot.append(submodElement)

        self.__configTree.write(
            self.__configFile,
            encoding="utf-8",
            pretty_print=True,
            xml_declaration=True,
        )

        self.__configTree = et.parse(self.__configFile)
        self.__configRoot = self.__configTree.getroot()
        self.__loadValuesFromConfig()

    def __loadValuesFromConfig(self) -> None:
        self.autoPlanetConnectionDistance = int(
            self.__configRoot.find("MaximumFleetMovementDistance").text
        )
        self.startingForcesLibraryURL = self.__configRoot.find(
            "StartingForcesLibraryURL"
        ).text

        mod_path_el = self.__configRoot.find("ModPath")

        if mod_path_el is not None and mod_path_el.text is not None:
            self.modPath = mod_path_el.text.strip()
        else:
            self.modPath = os.getcwd()

        # Submod names in ascending priority order (last = highest priority)
        self.submods = []
        for submodElement in self.__configRoot.findall("Submod"):
            if submodElement.text is not None:
                submodName = submodElement.text.strip()
                if submodName:
                    self.submods.append(submodName)

        self.dataFolders = [os.path.join(self.modPath, "Data")]
        for submod in self.submods:
            self.dataFolders.append(os.path.join(self.modPath, submod, "Data"))

        # dataPath remains the base Data folder for backward compatibility
        self.dataPath = self.dataFolders[0]

    def __setElementText(self, tag: str, value: str) -> None:
        element = self.__configRoot.find(tag)
        if element is None:
            element = et.Element(tag)
            self.__configRoot.append(element)
        element.text = value
