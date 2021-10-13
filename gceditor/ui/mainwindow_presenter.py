from abc import ABC, abstractmethod
from typing import Iterable, List, Protocol, Set, Dict, TypeVar, Union


from config import Config
from gceditor.gameObjects.gameObjectRepository import GameObjectRepository
from gceditor.gameObjects.planet import Planet
from gceditor.gameObjects.traderoute import TradeRoute
from gceditor.gameObjects.faction import Faction
from gceditor.gameObjects.campaign import Campaign
from gceditor.ui.galacticplot import GalacticPlot
from gceditor.RepositoryCreator import RepositoryCreator
from gceditor.xmlUtil.xmlwriter import XMLWriter
from gceditor.xmlUtil.xmlreader import XMLReader
from gceditor.xmlUtil.xmlstructure import XMLStructure


NamedGameObject = Union[Campaign, Planet, TradeRoute, Faction]
GameObjectIterable = Iterable[NamedGameObject]

NamedGamObjectTypeVar = TypeVar('NamedGamObjectTypeVar', bound=NamedGameObject)


class MainWindow(ABC):
    @abstractmethod
    def setMainWindowPresenter(self, presenter: 'MainWindowPresenter') -> None:
        raise NotImplementedError()

    @abstractmethod
    def addPlanets(self, planets: List[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def addTradeRoutes(self, tradeRoutes: List[str]) -> None:
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
        self._mainWindow: MainWindow = mainWindow
        self._plot: GalacticPlot = self._mainWindow.makeGalacticPlot()

        self._xmlWriter: XMLWriter = XMLWriter()

        self._repository = repository
        self._repositoryCreator = RepositoryCreator()

        self._config = config

        self.campaigns: List[Campaign] = list()
        self._planets: List[Planet] = list()
        self._tradeRoutes: List[TradeRoute] = list()
        self._availableTradeRoutes: List[TradeRoute] = list()
        self._newTradeRoutes: List[TradeRoute] = list()
        self._updatedPlanetCoords: Dict[str, List[float]] = dict()

        self._selectedCampaignIndex: int = 0

        self._checkedPlanets: Set[Planet] = set()
        self._checkedTradeRoutes: Set[TradeRoute] = set()

        self._showAutoConnections = True

        self._plot.planetSelectedSignal.connect(self.planetSelectedOnPlot)

        self._updateWidgets()

        self.newTradeRouteCommand = None
        self.campaignPropertiesCommand = None

    def onDataFolderChanged(self, folder: str) -> None:
        """Updates the repository and refreshes the main window when a new data folder is selected"""
        self._repository.emptyRepository()
        self._repository = self._repositoryCreator.constructRepository(folder)
        XMLStructure.dataFolder = folder

        self._updateWidgets()

    def onPlanetChecked(self, index: int, checked: bool) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        planet_at_index = self._planets[index]
        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        self._setPlanetState(planet_at_index, selected_campaign, checked)
        self._updateAvailableTradeRoutes(self._checkedPlanets)
        self._mainWindow.updatePlanetComboBox(self._getNames(self._checkedPlanets))
        self._updateGalacticPlot()

    def planetSelectedOnPlot(self, index: int) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""

        planet_at_index = self._planets[index]
        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        checked = planet_at_index not in self._checkedPlanets
        self._setPlanetState(planet_at_index, selected_campaign, checked)
        self._updateAvailableTradeRoutes(self._checkedPlanets)

        selectedPlanets = self._collectSelectedPlanetIndices()
        self._mainWindow.updatePlanetSelection(selectedPlanets)
        self._mainWindow.updatePlanetComboBox(self._getNames(self._checkedPlanets))
        self._updateGalacticPlot()

    def _collectSelectedPlanetIndices(self):
        return [index for index, planet in enumerate(self._planets) 
                if planet in self._checkedPlanets]

    def _setPlanetState(self, planet: Planet, selected_campaign: Campaign, checked: bool) -> None:
        if checked:
            self._checkedPlanets.add(planet)
            selected_campaign.planets.add(planet)
        elif planet in self._checkedPlanets:
            self._checkedPlanets.remove(planet)
            selected_campaign.planets.remove(planet)

    def onTradeRouteChecked(self, index: int, checked: bool) -> None:
        """If a trade route is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        checked_traderoute = self._availableTradeRoutes[index]
        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        self._setTradeRouteState(checked_traderoute, selected_campaign, checked)
        self._updateGalacticPlot()

    def _setTradeRouteState(self, traderoute: TradeRoute, selected_campaign: Campaign, checked: bool) -> None:
        if checked:
            self._checkedTradeRoutes.add(traderoute)
            selected_campaign.tradeRoutes.add(traderoute)
        elif traderoute in self._checkedTradeRoutes:
            self._checkedTradeRoutes.remove(traderoute)
            selected_campaign.tradeRoutes.remove(traderoute)

    def onCampaignSelected(self, index: int) -> None:
        """If a campaign is selected by the user, clear then refresh the galaxy plot"""
        self._checkedPlanets.clear()
        self._checkedTradeRoutes.clear()

        self._selectedCampaignIndex = index

        campaign_planets = self.campaigns[index].planets
        if campaign_planets is not None:
            self._updateSelectedPlanets(index)

        self._updateAvailableTradeRoutes(campaign_planets)

        self._mainWindow.updatePlanetComboBox(self._getNames(self._checkedPlanets))
        self._updateGalacticPlot()

    def onNewCampaign(self, campaign: Campaign) -> None:
        """If a new campaign is created, add the campaign to the repository, and clear then refresh the galaxy plot"""
        self._repository.addCampaign(campaign)

        self._updateWidgets()

        self._mainWindow.updateCampaignComboBox(
            self._getNames(self.campaigns), campaign.name
        )

    def onNewTradeRoute(self, tradeRoute: TradeRoute):
        """Handles new trade routes"""
        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        self._repository.addTradeRoute(tradeRoute)
        self._newTradeRoutes.append(tradeRoute)

        if all(planet in self._checkedPlanets for planet in (tradeRoute.start, tradeRoute.end)):
            self._checkedTradeRoutes.add(tradeRoute)

        selected_campaign.tradeRoutes.add(tradeRoute)
        self._updateWidgets()

    def onAutoConnectionSettingChanged(
        self, newAutoConnectionDistance, showAutoConnections
    ):
        self._config.autoPlanetConnectionDistance = newAutoConnectionDistance
        self._showAutoConnections = showAutoConnections
        self._updateGalacticPlot()

    def onPlanetPositionChanged(self, name, new_x, new_y) -> None:
        """Updates position of a planet in the repository"""
        planet = self._repository.getPlanetByName(name)
        planet.x = new_x
        planet.y = new_y
        self._updatedPlanetCoords[name] = [new_x, new_y]
        self._updateGalacticPlot()

    def allPlanetsChecked(self, checked: bool) -> None:
        """Select all planets handler: plots all planets"""
        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        if checked:
            self._checkedPlanets.update(self._planets)
            selected_campaign.planets.update(self._checkedPlanets)
        else:
            self._checkedPlanets.clear()
            selected_campaign.planets.clear()

        self._mainWindow.updatePlanetComboBox(self._getNames(self._checkedPlanets))
        self._updateAvailableTradeRoutes(self._checkedPlanets)
        self._updateGalacticPlot()

    def allTradeRoutesChecked(self, checked: bool) -> None:
        """Select all trade routes handler: plots all trade routes"""
        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        if checked:
            self._checkedTradeRoutes.update(self._availableTradeRoutes)
            selected_campaign.tradeRoutes.update(self._availableTradeRoutes)
        else:
            self._checkedTradeRoutes.clear()
            selected_campaign.tradeRoutes.clear()

        self._updateGalacticPlot()

    def saveFile(self, fileName: str) -> None:
        """Saves XML files"""
        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        selected_campaign.planets = self._checkedPlanets
        selected_campaign.tradeRoutes = self._checkedTradeRoutes
        self._xmlWriter.campaignWriter(selected_campaign, fileName)

        if self._newTradeRoutes:
            self._xmlWriter.tradeRouteWriter(self._newTradeRoutes)

        if self._updatedPlanetCoords:
            xmlReader = XMLReader()
            gameObjectFile = XMLStructure.dataFolder + "/XML/GameObjectFiles.XML"
            planetRoots = xmlReader.findPlanetFilesAndRoots(gameObjectFile)
            self._xmlWriter.planetCoordinatesWriter(
                XMLStructure.dataFolder + "/XML/",
                planetRoots,
                self._updatedPlanetCoords,
            )

    def getNameOfPlanetAt(self, ind: int) -> str:
        return self._planets[ind].name

    def getPositionOfPlanetAt(self, ind: int):
        return self._planets[ind].x, self._planets[ind].y

    def _getNames(self, inputList: GameObjectIterable) -> List[str]:
        """Returns the name attribute from a list of GameObjects"""
        return [x.name for x in inputList]

    def _updateWidgets(self) -> None:
        """Update the main window widgets"""
        self.campaigns = self._sortedByName(self._repository.campaigns)
        self._planets = self._sortedByName(self._repository.planets)
        self._tradeRoutes = self._sortedByName(self._repository.tradeRoutes)
        self._factions: List[Faction] = self._sortedByName(self._repository.factions)

        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        self._updateAvailableTradeRoutes(selected_campaign.planets)

        self._mainWindow.emptyWidgets()
        self._mainWindow.addCampaigns(self._getNames(self.campaigns))
        self._mainWindow.addPlanets(self._getNames(self._planets))
        self._mainWindow.addTradeRoutes(self._getNames(self._availableTradeRoutes))

        self._mainWindow.updateCampaignComboBoxSelection(self._selectedCampaignIndex)
        self.onCampaignSelected(self._selectedCampaignIndex)

        self._mainWindow.updatePlanetComboBox(self._getNames(self._checkedPlanets))

        self._updateSelectedTradeRoutes(self._selectedCampaignIndex)

        self._updateGalacticPlot()

    def _sortedByName(self, objects: Iterable[NamedGamObjectTypeVar]) -> List[NamedGamObjectTypeVar]:
        return sorted(objects, key=lambda entry: entry.name)

    def _updateSelectedPlanets(self, index: int) -> None:
        """Update the selected trade routes for the currently selected campaign"""
        selectedPlanets = []

        self._checkedPlanets.update(self.campaigns[index].planets)

        for p in self._checkedPlanets:
            selectedPlanets.append(self._planets.index(p))

        self._mainWindow.updatePlanetSelection(selectedPlanets)

    def _updateSelectedTradeRoutes(self, index: int) -> None:
        """Update the selected planets for the currently selected campaign"""
        selectedTradeRoutes = []

        self._checkedTradeRoutes = self.campaigns[index].tradeRoutes.intersection(
            self._availableTradeRoutes
        )

        for t in self._checkedTradeRoutes:
            selectedTradeRoutes.append(self._availableTradeRoutes.index(t))

        self._mainWindow.updateTradeRouteSelection(selectedTradeRoutes)

    def _updateAvailableTradeRoutes(self, planets: Iterable[Planet]):
        """Updates the list of available trade routes based on the planets in the GC"""
        privateAvailableTradeRoutes = set([
            tr for tr in self._tradeRoutes 
            if tr.start in planets and tr.end in planets
        ])
            

        if self._newTradeRoutes:
            # Ensure any new routes are appended to the available list for immediate use
            privateAvailableTradeRoutes.update(self._newTradeRoutes)

        selected_campaign = self.campaigns[self._selectedCampaignIndex]
        selected_campaign.tradeRoutes = selected_campaign.tradeRoutes.intersection(privateAvailableTradeRoutes)

        self._availableTradeRoutes = sorted(
            privateAvailableTradeRoutes, key=lambda entry: entry.name
        )
        self._mainWindow.updateTradeRoutes(
            self._getNames(self._availableTradeRoutes)
        )
        self._updateSelectedTradeRoutes(self._selectedCampaignIndex)

    def _updateGalacticPlot(self):
        autoConnectionDistance = self.config.autoPlanetConnectionDistance
        if not self._showAutoConnections:
            autoConnectionDistance = 0
        self._plot.plotGalaxy(
            self._checkedPlanets,
            self._checkedTradeRoutes,
            self._planets,
            autoConnectionDistance,
        )

    @property
    def config(self):
        return self._config

    @property
    def showAutoConnections(self):
        return self._showAutoConnections
