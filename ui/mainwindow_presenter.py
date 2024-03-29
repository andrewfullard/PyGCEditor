from abc import ABC, abstractmethod
from typing import List, Set, Dict
from xmlTools.xmlreader import XMLReader
from xmlTools.xmlwriter import XMLWriter
import pandas as pd

from config import Config
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.faction import Faction
from gameObjects.campaign import Campaign
from ui.galacticplot import GalacticPlot
from RepositoryCreator import RepositoryCreator
from xmlTools.xmlstructure import XMLStructure
from DisplayHelpers import DisplayHelpers


class MainWindowPresenter:
    pass


class MainWindow(ABC):
    @abstractmethod
    def setMainWindowPresenter(self, presenter: MainWindowPresenter) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addPlanets(self, planets: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addFactions(self, factions: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addTradeRoutes(self, tradeRoutes: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateTradeRoutes(self, tradeRoutes: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addCampaigns(self, campaigns: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def makeGalacticPlot(self) -> GalacticPlot:
        raise NotImplementedError()

    @abstractmethod
    def emptyWidgets(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateCampaignComboBox(self, campaigns: List[str], newCampaign: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateCampaignComboBoxSelection(self, index: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updatePlanetComboBox(self, planets: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updatePlanetSelection(self, planets: List[Planet]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateTradeRouteSelection(self, tradeRoutes: List[TradeRoute]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def selectSingleTradeRoute(self, index: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateFactionSelection(self, factions: List[Faction]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updatePlanetInfoDisplay(
        self, planet: Planet, startingForces: pd.DataFrame(),
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updatePlanetCountDisplay(self, planets: List[Planet]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def updateTotalFactionIncome(self, entry: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def clearPlanets(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def clearTradeRoutes(self) -> None:
        raise NotImplementedError()


class MainWindowPresenter:
    """Window display class"""

    def __init__(
        self, mainWindow: MainWindow, repository: GameObjectRepository, config: Config
    ):
        self.__mainWindow: MainWindow = mainWindow
        self.__plot: GalacticPlot = self.__mainWindow.makeGalacticPlot()

        self.__xmlWriter: XMLWriter = XMLWriter()

        self.__repository = repository
        self.__repositoryCreator = RepositoryCreator()

        self.__config = config

        self.campaigns: List[Campaign] = list()
        self.__planets: List[Planet] = list()
        self.__planetOwners: List[Faction] = list()
        self.__playableFactions: List[Faction] = list()
        self.__tradeRoutes: List[TradeRoute] = list()
        self.__availableTradeRoutes: List[TradeRoute] = list()
        self.__newTradeRoutes: List[TradeRoute] = list()
        self.__updatedPlanetCoords: Dict[str, List[float]] = dict()

        self.__selectedCampaignIndex: int = 0

        self.__checkedPlanets: Set[Planet] = set()
        self.__checkedPlayableFactions: Set[Faction] = set()
        self.__checkedTradeRoutes: Set[TradeRoute] = set()

        self.__showAutoConnections = True

        self.__plot.planetSelectedSignal.connect(self.planetSelectedOnPlot)
        self.__plot.planetShiftSelectedSignal.connect(self.planetShiftSelectedOnPlot)

        self.__helper = DisplayHelpers(self.__repository, self.campaigns)

        self.__updateWidgets()

        self.__onPlotSelectedStartPlanet = None
        self.__onPlotSelectedEndPlanet = None

        self.newTradeRouteCommand = None
        self.campaignPropertiesCommand = None

    def importStartingForces(self) -> None:
        """Imports all starting forces from spreadsheets"""
        self.getSelectedCampaign().startingForces = (
            self.__repository.startingForcesLibrary
        )

    def importStartingForcesAll(self) -> None:
        """Imports all starting forces from spreadsheets into ALL GCs"""
        for i, campaign in enumerate(self.campaigns):
            campaign.startingForces = (
                self.__repository.startingForcesLibrary
            )
            self.campaigns[i] = campaign

    def onDataFolderChanged(self, folder: str) -> None:
        """Updates the repository and refreshes the main window when a new data folder is selected"""
        self.__repository.emptyRepository()
        print("Loading from folder " + folder)
        self.__repository = self.__repositoryCreator.constructRepository(
            folder, self.__config.startingForcesLibraryURL
        )
        XMLStructure.dataFolder = folder

        self.__updateWidgets()

    def onPlanetChecked(self, index: int, checked: bool) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        if checked:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__checkedPlanets.add(self.__planets[index])
                self.getSelectedCampaign().planets.add(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        else:
            if self.__planets[index] in self.__checkedPlanets:
                self.__checkedPlanets.remove(self.__planets[index])
                self.getSelectedCampaign().planets.remove(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__planetOwners = self.__helper.getPlanetOwners(
            self.__selectedCampaignIndex, self.__checkedPlanets
        )
        self.__mainWindow.updateTotalFactionIncome(self.__helper.calculateFactionIncome(self.getSelectedCampaign().planets, self.__planetOwners))
        self.__updateGalacticPlot()

    def planetSelectedOnPlot(self, index: int) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        if self.__planets[index] not in self.__checkedPlanets:
            self.__checkedPlanets.add(self.__planets[index])
            self.getSelectedCampaign().planets.add(self.__planets[index])
            self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        elif self.__planets[index] in self.__checkedPlanets:
            self.__checkedPlanets.remove(self.__planets[index])
            self.getSelectedCampaign().planets.remove(self.__planets[index])
            self.__updateAvailableTradeRoutes(self.__checkedPlanets)

        selectedPlanets = []

        for p in self.__checkedPlanets:
            selectedPlanets.append(self.__getNames(self.__planets).index(p.name))

        self.__mainWindow.updatePlanetSelection(selectedPlanets)
        self.__planetOwners = self.__helper.getPlanetOwners(
            self.__selectedCampaignIndex, self.__checkedPlanets
        )
        self.__mainWindow.updateTotalFactionIncome(self.__helper.calculateFactionIncome(self.getSelectedCampaign().planets, self.__planetOwners))
        self.__mainWindow.updatePlanetCountDisplay(selectedPlanets)
        self.__mainWindow.updatePlanetMaxConnectionsCountDisplay(self.__checkedTradeRoutes)
        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__updateGalacticPlot()

    def planetShiftSelectedOnPlot(self, index: int) -> None:
        """If two planets in a row are right clicked by a user, this find and adds the trade route, or helps create a new one"""
        if not self.__onPlotSelectedStartPlanet:
            self.__onPlotSelectedStartPlanet = self.__planets[index]
            self.__plot.TraceTradeRoute(index)
            return
        
        if self.__onPlotSelectedStartPlanet and not self.__onPlotSelectedEndPlanet:
            self.__onPlotSelectedEndPlanet = self.__planets[index]
            self.__plot.TraceTradeRoute(None)

        if self.__onPlotSelectedStartPlanet and self.__onPlotSelectedEndPlanet:
            if not self.__onPlotSelectedStartPlanet == self.__onPlotSelectedEndPlanet:
                try:
                    traderoute = self.__repository.getTradeRouteByPlanets(self.__onPlotSelectedStartPlanet, self.__onPlotSelectedEndPlanet)
                    try:
                        index = self.__availableTradeRoutes.index(traderoute)
                    except ValueError:
                        print("Error, trade route not available but it should be! Try turning a planet off and on")

                    if self.__mainWindow.selectSingleTradeRoute(index):
                        self.onTradeRouteChecked(index, True)
                    else:
                        self.onTradeRouteChecked(index, False)
                except RuntimeError:
                    self.newTradeRouteCommand.execute(start = self.__onPlotSelectedStartPlanet.name, end = self.__onPlotSelectedEndPlanet.name)
            
            self.__onPlotSelectedStartPlanet = None
            self.__onPlotSelectedEndPlanet = None
 
            self.__updateGalacticPlot()
            

    def onTradeRouteChecked(self, index: int, checked: bool) -> None:
        """If a trade route is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        if checked:
            if self.__availableTradeRoutes[index] not in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.add(self.__availableTradeRoutes[index])
                self.getSelectedCampaign().tradeRoutes.add(
                    self.__availableTradeRoutes[index]
                )
        else:
            if self.__availableTradeRoutes[index] in self.__checkedTradeRoutes:
                self.__checkedTradeRoutes.remove(self.__availableTradeRoutes[index])
                self.getSelectedCampaign().tradeRoutes.remove(
                    self.__availableTradeRoutes[index]
                )

        self.__mainWindow.updatePlanetMaxConnectionsCountDisplay(self.__checkedTradeRoutes)
        self.__updateGalacticPlot()

    def onFactionChecked(self, index: int, checked: bool) -> None:
        """If a faction is checked by the user, add it to the selected campaign"""
        if checked:
            if self.__playableFactions[index] not in self.__checkedPlayableFactions:
                self.__checkedPlayableFactions.add(self.__playableFactions[index])
                self.getSelectedCampaign().playableFactions.add(self.__playableFactions[index])
        else:
            if self.__playableFactions[index] in self.__checkedPlayableFactions:
                self.__checkedPlayableFactions.remove(self.__playableFactions[index])
                self.getSelectedCampaign().playableFactions.remove(self.__playableFactions[index])

    def onCampaignSelected(self, index: int) -> None:
        """If a campaign is selected by the user, clear then refresh the galaxy plot"""
        if index < 0:
            return
        self.__checkedPlanets.clear()
        self.__checkedTradeRoutes.clear()
        self.__checkedPlayableFactions.clear()

        self.__selectedCampaignIndex = index

        selectedCampaign = self.getSelectedCampaign()

        selectedPlanets = []
        selectedTradeRoutes = []
        selectedFactions = []

        self.__helper = DisplayHelpers(self.__repository, self.campaigns)

        if selectedCampaign.planets is not None:
            self.__checkedPlanets.update(selectedCampaign.planets)

            for p in self.__checkedPlanets:
                selectedPlanets.append(self.__planets.index(p))

            self.__mainWindow.updatePlanetSelection(selectedPlanets)
            self.__mainWindow.updatePlanetCountDisplay(selectedPlanets)

        self.__updateAvailableTradeRoutes(selectedCampaign.planets)

        if selectedCampaign.tradeRoutes is not None:
            self.__checkedTradeRoutes.update(selectedCampaign.tradeRoutes)
            missingRoutes = set()

            for t in self.__checkedTradeRoutes:
                if t is not None:
                    try:
                        selectedTradeRoutes.append(self.__availableTradeRoutes.index(t))
                    except (ValueError):
                        print("The trade route " + t.name + " is missing!")
                else:
                    missingRoutes.add(t)
                    print("Trade route missing!")

            # Remove missing routes to allow plotting
            self.__checkedTradeRoutes -= missingRoutes

            self.__mainWindow.updateTradeRouteSelection(selectedTradeRoutes)
            self.__mainWindow.updatePlanetMaxConnectionsCountDisplay(self.__checkedTradeRoutes)

        self.__planetOwners = self.__helper.getPlanetOwners(
            index, self.__checkedPlanets
        )

        self.__mainWindow.updateTotalFactionIncome(self.__helper.calculateFactionIncome(selectedCampaign.planets, self.__planetOwners))

        if selectedCampaign.playableFactions is not None:
            self.__checkedPlayableFactions.update(selectedCampaign.playableFactions)

            for f in self.__checkedPlayableFactions:
                selectedFactions.append(self.__factions.index(f))

            self.__mainWindow.updateFactionSelection(selectedFactions)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__updateGalacticPlot()

    def getSelectedCampaign(self) -> Campaign:
        if self.__selectedCampaignIndex > -1:
            return self.campaigns[self.__selectedCampaignIndex]

        return None

    def onNewCampaign(self, campaign: Campaign) -> None:
        """If a new campaign is created, add the campaign to the repository, and clear then refresh the galaxy plot"""
        self.__repository.addCampaign(campaign)

        self.__updateWidgets()

        self.__mainWindow.updateCampaignComboBox(
            [x.setName for x in self.campaigns], campaign.setName
        )

    def onCampaignUpdate(self, campaign: Campaign) -> None:
        """If a campaign is updated, update it and add the campaign to the repository, and clear then refresh the galaxy plot"""
        self.__repository.removeCampaign(campaign)
        self.__repository.addCampaign(campaign)

        self.__updateWidgets()
        self.__mainWindow.updateCampaignComboBox(
            [x.setName for x in self.campaigns], campaign.setName
        )

    def onAutoConnectionSettingChanged(
        self, newAutoConnectionDistance, showAutoConnections
    ):
        self.__config.autoPlanetConnectionDistance = newAutoConnectionDistance
        self.__showAutoConnections = showAutoConnections
        self.__updateGalacticPlot()

    def onNewTradeRoute(self, tradeRoute: TradeRoute):
        """Handles new trade routes"""
        self.__repository.addTradeRoute(tradeRoute)
        self.__newTradeRoutes.append(tradeRoute)

        if (
            tradeRoute.start in self.__checkedPlanets
            or tradeRoute.end in self.__checkedPlanets
        ):
            self.__checkedTradeRoutes.add(tradeRoute)

        self.getSelectedCampaign().tradeRoutes.add(tradeRoute)
        self.__updateWidgets()

    def onPlanetSelected(self, entry: str) -> None:
        """If a planet is selected by the user, display the associated starting forces and planet info"""
        planet = self.__repository.getPlanetByName(entry)

        campaignForces = self.getSelectedCampaign().startingForces
        try:
            campaignForces["Planet"] == entry
        except KeyError:
            self.__mainWindow.updatePlanetInfoDisplay(planet, None, filter=False)
            return

        self.__mainWindow.updatePlanetInfoDisplay(planet, campaignForces, filter=entry)

    def onPlanetPositionChanged(self, name, new_x, new_y) -> None:
        """Updates position of a planet in the repository"""
        planet = self.__repository.getPlanetByName(name)
        planet.x = new_x
        planet.y = new_y
        self.__updatedPlanetCoords[name] = [new_x, new_y]
        self.__updateGalacticPlot()

    def allPlanetsChecked(self, checked: bool) -> None:
        """Select all planets handler: plots all planets"""
        if checked:
            self.__checkedPlanets.update(self.__planets)
            self.getSelectedCampaign().planets.update(self.__planets)
        else:
            self.__checkedPlanets.clear()
            self.getSelectedCampaign().planets.clear()

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        self.__updateGalacticPlot()

    def allTradeRoutesChecked(self, checked: bool) -> None:
        """Select all trade routes handler: plots all trade routes"""
        if checked:
            self.__checkedTradeRoutes.update(self.__availableTradeRoutes)
            self.getSelectedCampaign().tradeRoutes.update(self.__availableTradeRoutes)
        else:
            self.__checkedTradeRoutes.clear()
            self.getSelectedCampaign().tradeRoutes.clear()

        self.__updateGalacticPlot()

    def saveFile(self, fileName: str) -> None:
        """Saves XML files"""
        campaign = self.getSelectedCampaign()
        factions = self.__repository.factions
        self.__xmlWriter.campaignWriter(campaign, factions, fileName)

        if len(self.__newTradeRoutes) > 0:
            self.__xmlWriter.tradeRouteWriter(self.__newTradeRoutes)

        if len(self.__updatedPlanetCoords) > 0:
            xmlReader = XMLReader()
            gameObjectFile = XMLStructure.dataFolder + "/XML/GameObjectFiles.XML"
            planetRoots = xmlReader.findPlanetFilesAndRoots(gameObjectFile)
            self.__xmlWriter.planetCoordinatesWriter(
                XMLStructure.dataFolder + "/XML/",
                planetRoots,
                self.__updatedPlanetCoords,
            )

    def saveAllCampaigns(self, default_forces_only=False) -> None:
        """Saves all campaigns to files

        Parameters
        ----------
        default_forces_only : bool, optional
            If True, only save campaigns that specify that they use
            default starting forces, by default False
        """        
        factions = self.__repository.factions
        for campaign in self.campaigns:
            if default_forces_only and campaign.useDefaultForces:
                self.__xmlWriter.campaignWriter(campaign, factions, campaign.fileName)
            elif not default_forces_only:
                self.__xmlWriter.campaignWriter(campaign, factions, campaign.fileName)

    def getNameOfPlanetAt(self, ind: int) -> str:
        return self.__planets[ind].name

    def getPositionOfPlanetAt(self, ind: int):
        return self.__planets[ind].x, self.__planets[ind].y

    def __getNames(self, inputList: list) -> List[str]:
        """Returns the name attribute from a list of GameObjects"""
        return [x.name for x in inputList]

    def __updateWidgets(self) -> None:
        """Update the main window widgets"""
        self.campaigns: List[Campaign] = sorted(
            self.__repository.campaigns, key=lambda entry: entry.name
        )
        self.__planets: List[Planet] = sorted(
            self.__repository.planets, key=lambda entry: entry.name
        )
        self.__tradeRoutes: List[TradeRoute] = sorted(
            self.__repository.tradeRoutes, key=lambda entry: entry.name
        )
        self.__playableFactions: List[Faction] = sorted(
            self.__repository.factions, key=lambda entry: entry.name
        )
        self.__factions: List[Faction] = sorted(
            self.__repository.factions, key=lambda entry: entry.name
        )

        selectedCampaign = self.getSelectedCampaign()
        if selectedCampaign:
            self.__updateAvailableTradeRoutes(selectedCampaign.planets)

        self.__mainWindow.emptyWidgets()

        self.__mainWindow.addCampaigns([x.setName for x in self.campaigns])
        self.__mainWindow.addPlanets(self.__getNames(self.__planets))
        self.__mainWindow.addFactions(self.__getNames(self.__factions))
        self.__mainWindow.addTradeRoutes(self.__getNames(self.__availableTradeRoutes))

        self.__mainWindow.updateCampaignComboBoxSelection(self.__selectedCampaignIndex)
        self.onCampaignSelected(self.__selectedCampaignIndex)

        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))

        self.__updateSelectedTradeRoutes(self.__selectedCampaignIndex)
        self.__updateSelectedFactions(self.__selectedCampaignIndex)

        self.__updateGalacticPlot()

    def __updateSelectedPlanets(self, index: int) -> None:
        """Update the selected planets for the currently selected campaign"""
        selectedPlanets = []

        self.__checkedPlanets.update(self.campaigns[index].planets)

        for p in self.__checkedPlanets:
            selectedPlanets.append(self.__planets.index(p))

        self.__mainWindow.updatePlanetSelection(selectedPlanets)

    def __updateSelectedTradeRoutes(self, index: int) -> None:
        """Update the selected planets for the currently selected campaign"""
        selectedTradeRoutes = []

        self.__checkedTradeRoutes = self.campaigns[index].tradeRoutes.intersection(
            self.__availableTradeRoutes
        )

        for t in self.__checkedTradeRoutes:
            selectedTradeRoutes.append(self.__availableTradeRoutes.index(t))

        self.__mainWindow.updateTradeRouteSelection(selectedTradeRoutes)

    def __updateAvailableTradeRoutes(self, planetList: list):
        """Updates the list of available trade routes based on the planets in the GC"""
        privateAvailableTradeRoutes = set(
            filter(
                lambda tr: (tr.start in planetList and tr.end in planetList),
                self.__tradeRoutes,
            )
        )

        if len(self.__newTradeRoutes) > 0:
            # Ensure any new routes are appended to the available list for immediate use
            privateAvailableTradeRoutes.update(self.__newTradeRoutes)

        self.campaigns[self.__selectedCampaignIndex].tradeRoutes = self.campaigns[
            self.__selectedCampaignIndex
        ].tradeRoutes.intersection(privateAvailableTradeRoutes)

        self.__availableTradeRoutes = sorted(
            privateAvailableTradeRoutes, key=lambda entry: entry.name
        )
        self.__mainWindow.updateTradeRoutes(
            self.__getNames(self.__availableTradeRoutes)
        )
        self.__updateSelectedTradeRoutes(self.__selectedCampaignIndex)


    def __updateSelectedFactions(self, index: int) -> None:
        """Update the selected factions for the currently selected campaign"""
        selectedFactions = []

        self.__checkedPlayableFactions.update(self.campaigns[index].playableFactions)

        for f in self.__checkedPlayableFactions:
            selectedFactions.append(self.__factions.index(f))

        self.__mainWindow.updateFactionSelection(selectedFactions)


    def __updateGalacticPlot(self):
        autoConnectionDistance = self.config.autoPlanetConnectionDistance
        if not self.__showAutoConnections:
            autoConnectionDistance = 0
        self.__plot.plotGalaxy(
            self.__checkedPlanets,
            self.__checkedTradeRoutes,
            self.__planets,
            self.__planetOwners,
            autoPlanetConnectionDistance=autoConnectionDistance,
        )

    @property
    def config(self):
        return self.__config

    @property
    def showAutoConnections(self):
        return self.__showAutoConnections
