import logging
from typing import List, Optional, Set, Dict
import os
import pandas as pd
from xmlTools.xmlreader import XMLReader
from xmlTools.xmlwriter import XMLWriter

from config import Config
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import CORE_ART_MODEL_NAME, Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.faction import Faction
from gameObjects.campaign import Campaign
from ui.qtgalacticplot import QtGalacticPlot
from RepositoryCreator import RepositoryCreator
from xmlTools.xmlstructure import XMLStructure
from DisplayHelpers import DisplayHelpers
from ui.DialogFactory import DialogFactory


logger = logging.getLogger(__name__)


class MainWindowPresenter:
    """Window display class"""

    def __init__(
        self,
        mainWindow,
        repository: GameObjectRepository,
        config: Config,
        dialogFactory: Optional[DialogFactory] = None,
    ):
        self.__mainWindow = mainWindow
        self.__plot: QtGalacticPlot = self.__mainWindow.makeGalacticPlot()

        self.__xmlWriter: XMLWriter = XMLWriter()

        self.__repository = repository
        self.__repositoryCreator = RepositoryCreator()
        self.__dialogFactory = dialogFactory

        self.__config = config

        self.campaigns: List[Campaign] = list()
        self.__planets: List[Planet] = list()
        self.__planetOwners: List[Faction] = list()
        self.__playableFactions: List[Faction] = list()
        self.__tradeRoutes: List[TradeRoute] = list()
        self.__availableTradeRoutes: List[TradeRoute] = list()
        self.__newTradeRoutes: List[TradeRoute] = list()
        self.__updatedPlanetCoords: Dict[str, List[float]] = dict()
        self.__undoHistory: List[dict] = []

        self.__selectedCampaignIndex: int = 0

        self.__checkedPlanets: Set[Planet] = set()
        self.__checkedPlayableFactions: Set[Faction] = set()
        self.__checkedTradeRoutes: Set[TradeRoute] = set()

        self.__showAutoConnections = True

        self.__plot.planetSelectedSignal.connect(self.planetSelectedOnPlot)
        self.__plot.planetShiftSelectedSignal.connect(self.planetShiftSelectedOnPlot)

        self.__helper = DisplayHelpers(self.__repository, self.campaigns)
        self.__plot.setDarkMode(self.__config.darkMap)

        self.__updateWidgets()

        self.__onPlotSelectedStartPlanet = None
        self.__onPlotSelectedEndPlanet = None

        self.newTradeRouteCommand = None
        self.campaignPropertiesCommand = None
        self.optionsDialogCommand = None

    def importStartingForces(self) -> None:
        """Imports all starting forces from spreadsheets"""
        self.__recordUndo()
        self.getSelectedCampaign().startingForces = (
            self.__repository.startingForcesLibrary
        )
        self.__refreshForcesDisplay()
        self.__syncPlanetDependentDisplays(False)

    def importStartingForcesAll(self) -> None:
        """Imports all starting forces from spreadsheets into ALL GCs"""
        self.__recordUndo()
        for i, campaign in enumerate(self.campaigns):
            campaign.startingForces = self.__repository.startingForcesLibrary
            self.campaigns[i] = campaign

    def onDataFolderChanged(self, modPath: str) -> None:
        """Updates the repository and refreshes the main window when a new mod folder is selected"""
        self.__repository.emptyRepository()
        logger.info("Loading from folder %s", modPath)
        dataFolders = [os.path.join(modPath, "Data")]
        for submod in self.__config.submods:
            submodPath = (
                submod
                if os.path.isabs(submod)
                else os.path.join(modPath, submod)
            )
            dataFolders.append(os.path.join(submodPath, "Data"))
        self.__repository = self.__repositoryCreator.constructRepository(
            dataFolders, self.__config.startingForcesLibraryURL
        )
        if self.__dialogFactory is not None:
            self.__dialogFactory.setRepository(self.__repository)
        self.__updateWidgets()

    def onConfigChanged(
        self,
        modPath: str,
        submods: List[str],
        autoPlanetConnectionDistance: int,
        startingForcesLibraryURL: str,
        darkMap: bool,
    ) -> None:
        """Persist config updates and refresh repository data folders if needed."""
        oldDataFolders = list(self.__config.dataFolders)

        self.__config.save(
            modPath,
            submods,
            autoPlanetConnectionDistance,
            startingForcesLibraryURL,
            darkMap,
        )
        self.__plot.setDarkMode(darkMap)

        if self.__config.dataFolders != oldDataFolders:
            self.__repository.emptyRepository()
            self.__repository = self.__repositoryCreator.constructRepository(
                self.__config.dataFolders,
                self.__config.startingForcesLibraryURL,
            )
            if self.__dialogFactory is not None:
                self.__dialogFactory.setRepository(self.__repository)
            self.__updateWidgets()
            return

        self.__updateGalacticPlot()

    def onPlanetChecked(self, index: int, checked: bool) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        if checked:
            if self.__planets[index] not in self.__checkedPlanets:
                self.__recordUndo()
                self.__checkedPlanets.add(self.__planets[index])
                self.getSelectedCampaign().planets.add(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        else:
            if self.__planets[index] in self.__checkedPlanets:
                self.__recordUndo()
                self.__checkedPlanets.remove(self.__planets[index])
                self.getSelectedCampaign().planets.remove(self.__planets[index])
                self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        self.__syncPlanetDependentDisplays(update_planet_count=False)
        self.__refreshForcesDisplay(preferredPlanetName=self.__planets[index].name)
        self.__updateGalacticPlot()

    def planetSelectedOnPlot(self, index: int) -> None:
        """If a planet is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        self.__recordUndo()
        planet = self.__mapPlanets[index]
        if planet not in self.__checkedPlanets:
            self.__checkedPlanets.add(planet)
            self.getSelectedCampaign().planets.add(planet)
            self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        elif planet in self.__checkedPlanets:
            self.__checkedPlanets.remove(planet)
            self.getSelectedCampaign().planets.remove(planet)
            self.__updateAvailableTradeRoutes(self.__checkedPlanets)

        selectedPlanets = []

        for p in self.__checkedPlanets:
            selectedPlanets.append(self.__getNames(self.__planets).index(p.name))

        self.__mainWindow.updatePlanetSelection(selectedPlanets)
        self.__syncPlanetDependentDisplays(update_planet_count=True)
        self.__mainWindow.updatePlanetMaxConnectionsCountDisplay(
            self.__checkedTradeRoutes
        )
        self.__refreshForcesDisplay(preferredPlanetName=planet.name)
        self.__updateGalacticPlot()

    def planetShiftSelectedOnPlot(self, index: int) -> None:
        """If two planets in a row are right clicked by a user, this find and adds the trade route, or helps create a new one"""
        planet = self.__mapPlanets[index]
        if not self.__onPlotSelectedStartPlanet:
            self.__onPlotSelectedStartPlanet = planet
            self.__plot.TraceTradeRoute(index)
            return

        if self.__onPlotSelectedStartPlanet and not self.__onPlotSelectedEndPlanet:
            self.__onPlotSelectedEndPlanet = planet
            self.__plot.TraceTradeRoute(None)

        if self.__onPlotSelectedStartPlanet and self.__onPlotSelectedEndPlanet:
            if not self.__onPlotSelectedStartPlanet == self.__onPlotSelectedEndPlanet:
                try:
                    traderoute = self.__repository.getTradeRouteByPlanets(
                        self.__onPlotSelectedStartPlanet, self.__onPlotSelectedEndPlanet
                    )
                    try:
                        index = self.__availableTradeRoutes.index(traderoute)
                    except ValueError:
                        logger.error(
                            "Trade route not available but it should be; try turning a planet off and on"
                        )

                    if self.__mainWindow.selectSingleTradeRoute(index):
                        self.onTradeRouteChecked(index, True)
                    else:
                        self.onTradeRouteChecked(index, False)
                except RuntimeError:
                    self.newTradeRouteCommand.execute(
                        start=self.__onPlotSelectedStartPlanet.name,
                        end=self.__onPlotSelectedEndPlanet.name,
                    )

            self.__onPlotSelectedStartPlanet = None
            self.__onPlotSelectedEndPlanet = None

            self.__updateGalacticPlot()

    def onTradeRouteChecked(self, index: int, checked: bool) -> None:
        """If a trade route is checked by the user, add it to the selected campaign and refresh the galaxy plot"""
        self.__recordUndo()
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

        self.__mainWindow.updatePlanetMaxConnectionsCountDisplay(
            self.__checkedTradeRoutes
        )
        self.__updateGalacticPlot()

    def onFactionChecked(self, index: int, checked: bool) -> None:
        """If a faction is checked by the user, add it to the selected campaign"""
        self.__recordUndo()
        if checked:
            if self.__playableFactions[index] not in self.__checkedPlayableFactions:
                self.__checkedPlayableFactions.add(self.__playableFactions[index])
                self.getSelectedCampaign().playableFactions.add(
                    self.__playableFactions[index]
                )
        else:
            if self.__playableFactions[index] in self.__checkedPlayableFactions:
                self.__checkedPlayableFactions.remove(self.__playableFactions[index])
                self.getSelectedCampaign().playableFactions.remove(
                    self.__playableFactions[index]
                )

    def onCampaignSelected(self, index: int) -> None:
        """If a campaign is selected by the user, clear then refresh the galaxy plot"""
        if index < 0:
            return
        self.__clearCheckedSelections()

        self.__selectedCampaignIndex = index

        selectedCampaign = self.getSelectedCampaign()

        self.__helper = DisplayHelpers(self.__repository, self.campaigns)

        self.__applyCampaignPlanets(selectedCampaign)
        self.__updateAvailableTradeRoutes(selectedCampaign.planets)
        self.__applyCampaignTradeRoutes(selectedCampaign)
        self.__applyCampaignFactions(selectedCampaign)
        self.__syncPlanetDependentDisplays(update_planet_count=False)
        self.__mainWindow.updatePlanetMaxConnectionsCountDisplay(
            self.__checkedTradeRoutes
        )
        self.__refreshForcesDisplay()
        self.__updateGalacticPlot()

    def getSelectedCampaign(self) -> Campaign:
        if 0 <= self.__selectedCampaignIndex < len(self.campaigns):
            return self.campaigns[self.__selectedCampaignIndex]

        return None

    def onNewCampaign(self, campaign: Campaign) -> None:
        """If a new campaign is created, add the campaign to the repository, and clear then refresh the galaxy plot"""
        self.__recordUndo()
        core_art_model = next(
            (
                planet
                for planet in self.__planets
                if planet.name == CORE_ART_MODEL_NAME
            ),
            None,
        )
        if core_art_model is not None:
            campaign.planets.add(core_art_model)
        self.__repository.addCampaign(campaign)

        self.__updateWidgets()

        self.__mainWindow.updateCampaignComboBox(
            [x.setName for x in self.campaigns], campaign.setName
        )

    def onCampaignUpdate(self, campaign: Campaign) -> None:
        """If a campaign is updated, update it and add the campaign to the repository, and clear then refresh the galaxy plot"""
        self.__recordUndo()
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
        self.__recordUndo()
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
        if not entry:
            self.__mainWindow.updatePlanetInfoDisplay(None, None, filter=False)
            return

        try:
            planet = self.__repository.getPlanetByName(entry)
        except RuntimeError:
            self.__mainWindow.updatePlanetInfoDisplay(None, None, filter=False)
            return

        campaignForces = self.getSelectedCampaign().startingForces
        if campaignForces is None or "Planet" not in campaignForces.columns:
            self.__mainWindow.updatePlanetInfoDisplay(planet, None, filter=False)
            return

        self.__mainWindow.updatePlanetInfoDisplay(planet, campaignForces, filter=entry)

    def onForcesTabActivated(self) -> None:
        """Refresh Forces tab displays when users switch back to it."""
        self.__refreshForcesDisplay()

    def onPlanetPositionChanged(self, name, new_x, new_y) -> None:
        """Updates position of a planet in the repository"""
        self.__recordUndo()
        planet = self.__repository.getPlanetByName(name)
        planet.x = new_x
        planet.y = new_y
        self.__updatedPlanetCoords[name] = [new_x, new_y]
        self.__updateGalacticPlot()

    def allPlanetsChecked(self, checked: bool) -> None:
        """Select all planets handler: plots all planets"""
        self.__recordUndo()
        if checked:
            self.__checkedPlanets.update(self.__planets)
            self.getSelectedCampaign().planets.update(self.__planets)
        else:
            self.__checkedPlanets.clear()
            self.getSelectedCampaign().planets.clear()

        self.__syncPlanetDependentDisplays(update_planet_count=True)
        self.__updateAvailableTradeRoutes(self.__checkedPlanets)
        self.__refreshForcesDisplay()
        self.__updateGalacticPlot()

    def allTradeRoutesChecked(self, checked: bool) -> None:
        """Select all trade routes handler: plots all trade routes"""
        self.__recordUndo()
        if checked:
            self.__checkedTradeRoutes.update(self.__availableTradeRoutes)
            self.getSelectedCampaign().tradeRoutes.update(self.__availableTradeRoutes)
        else:
            self.__checkedTradeRoutes.clear()
            self.getSelectedCampaign().tradeRoutes.clear()

        self.__updateGalacticPlot()

    def undo(self) -> None:
        """Undo the most recent edit, if one is available."""
        if not self.__undoHistory:
            return

        snapshot = self.__undoHistory.pop()
        for campaign in self.campaigns:
            self.__repository.removeCampaign(campaign)
        for campaign in snapshot["campaigns"]:
            self.__repository.addCampaign(campaign)
        self.campaigns = list(snapshot["campaigns"])

        for campaign, planets, routes, factions, starting_forces in snapshot[
            "campaign_states"
        ]:
            campaign.planets.clear()
            campaign.planets.update(planets)
            campaign.tradeRoutes.clear()
            campaign.tradeRoutes.update(routes)
            campaign.playableFactions.clear()
            campaign.playableFactions.update(factions)
            campaign.startingForces = starting_forces.copy()

        current_routes = self.__repository.tradeRoutes
        for route in current_routes - snapshot["trade_routes"]:
            self.__repository.removeTradeRoute(route)
        for route in snapshot["trade_routes"] - current_routes:
            self.__repository.addTradeRoute(route)
        for planet, x, y in snapshot["planet_positions"]:
            planet.x = x
            planet.y = y

        self.__newTradeRoutes = list(snapshot["new_trade_routes"])
        self.__updatedPlanetCoords = dict(snapshot["updated_planet_coords"])
        self.__selectedCampaignIndex = snapshot["selected_campaign_index"]
        self.__updateWidgets()

    def __recordUndo(self) -> None:
        campaign_states = [
            (
                campaign,
                set(campaign.planets),
                set(campaign.tradeRoutes),
                set(campaign.playableFactions),
                campaign.startingForces.copy(),
            )
            for campaign in self.campaigns
        ]
        self.__undoHistory.append(
            {
                "campaigns": list(self.campaigns),
                "campaign_states": campaign_states,
                "trade_routes": self.__repository.tradeRoutes,
                "planet_positions": [
                    (planet, planet.x, planet.y)
                    for planet in self.__repository.planets
                ],
                "new_trade_routes": list(self.__newTradeRoutes),
                "updated_planet_coords": dict(self.__updatedPlanetCoords),
                "selected_campaign_index": self.__selectedCampaignIndex,
            }
        )
        del self.__undoHistory[:-20]

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
        self.__mapPlanets: List[Planet] = [
            planet for planet in self.__planets if planet.mapVisible
        ]
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

        if not self.campaigns:
            self.__selectedCampaignIndex = -1
            self.__mainWindow.updateCampaignComboBoxSelection(-1)
            self.__mainWindow.updatePlanetComboBox([])
            self.__mainWindow.updateTradeRouteSelection([])
            self.__mainWindow.updateFactionSelection([])
            self.__updateGalacticPlot()
            return

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

    def __clearCheckedSelections(self) -> None:
        self.__checkedPlanets.clear()
        self.__checkedTradeRoutes.clear()
        self.__checkedPlayableFactions.clear()

    def __applyCampaignPlanets(self, campaign: Campaign) -> None:
        if campaign.planets is None:
            self.__mainWindow.updatePlanetSelection([])
            self.__mainWindow.updatePlanetCountDisplay([])
            return

        self.__checkedPlanets.update(campaign.planets)
        selectedPlanets = [self.__planets.index(p) for p in self.__checkedPlanets]
        self.__mainWindow.updatePlanetSelection(selectedPlanets)
        self.__mainWindow.updatePlanetCountDisplay(selectedPlanets)

    def __applyCampaignTradeRoutes(self, campaign: Campaign) -> None:
        if campaign.tradeRoutes is None:
            self.__mainWindow.updateTradeRouteSelection([])
            return

        self.__checkedTradeRoutes.update(campaign.tradeRoutes)
        missingRoutes = set()
        selectedTradeRoutes = []

        for t in self.__checkedTradeRoutes:
            if t is not None:
                try:
                    selectedTradeRoutes.append(self.__availableTradeRoutes.index(t))
                except ValueError:
                    logger.error("The trade route %s is missing!", t.name)
            else:
                missingRoutes.add(t)
                logger.error("Trade route missing!")

        self.__checkedTradeRoutes -= missingRoutes
        self.__mainWindow.updateTradeRouteSelection(selectedTradeRoutes)

    def __applyCampaignFactions(self, campaign: Campaign) -> None:
        if campaign.playableFactions is None:
            self.__mainWindow.updateFactionSelection([])
            return

        self.__checkedPlayableFactions.update(campaign.playableFactions)
        selectedFactions = [self.__factions.index(f) for f in self.__checkedPlayableFactions]
        self.__mainWindow.updateFactionSelection(selectedFactions)

    def __syncPlanetDependentDisplays(self, update_planet_count: bool) -> None:
        self.__mainWindow.updatePlanetComboBox(self.__getNames(self.__checkedPlanets))
        self.__planetOwners = self.__helper.getPlanetOwners(
            self.__selectedCampaignIndex, self.__checkedPlanets
        )
        self.__mainWindow.updateTotalFactionIncome(
            self.__helper.calculateFactionIncome(
                self.getSelectedCampaign().planets, self.__planetOwners
            )
        )

        if update_planet_count:
            selected_planets = []
            for p in self.__checkedPlanets:
                selected_planets.append(self.__getNames(self.__planets).index(p.name))
            self.__mainWindow.updatePlanetCountDisplay(selected_planets)

    def __refreshForcesDisplay(self, preferredPlanetName: Optional[str] = None) -> None:
        planetNames = sorted(self.__getNames(self.__checkedPlanets))
        self.__mainWindow.updatePlanetComboBox(planetNames)

        if not planetNames:
            self.__mainWindow.updatePlanetInfoDisplay(None, None, filter=False)
            return

        selectedPlanetName = preferredPlanetName or self.__mainWindow.getSelectedPlanetName()

        if selectedPlanetName not in planetNames:
            selectedPlanetName = planetNames[0]

        self.__mainWindow.updatePlanetComboBoxSelection(selectedPlanetName)
        self.onPlanetSelected(selectedPlanetName)

    def __updateAvailableTradeRoutes(self, planetList: list):
        """Updates the list of available trade routes based on the planets in the GC"""
        privateAvailableTradeRoutes = set(
            filter(
                lambda tr: tr.start in planetList and tr.end in planetList,
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
        mapPlanets = set(self.__checkedPlanets).intersection(self.__mapPlanets)
        mapPlanetOwners = (
            self.__helper.getPlanetOwners(self.__selectedCampaignIndex, mapPlanets)
            if self.campaigns
            else []
        )
        self.__plot.plotGalaxy(
            mapPlanets,
            self.__checkedTradeRoutes,
            self.__mapPlanets,
            mapPlanetOwners,
            autoPlanetConnectionDistance=autoConnectionDistance,
            allTradeRoutes=self.__tradeRoutes,
        )

    @property
    def config(self):
        return self.__config

    @property
    def showAutoConnections(self):
        return self.__showAutoConnections
