import pandas as pd

from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter


class FakeSignal:
    def connect(self, callback):
        self.callback = callback


class FakePlot:
    def __init__(self):
        self.planetSelectedSignal = FakeSignal()
        self.planetShiftSelectedSignal = FakeSignal()

    def plotGalaxy(self, *args, **kwargs):
        pass


class FakeConfig:
    autoPlanetConnectionDistance = 0


class FakeMainWindow(MainWindow):
    def __init__(self):
        self.combo_planets = []
        self.selected_planet = ""

    def setMainWindowPresenter(self, presenter):
        pass

    def addPlanets(self, planets):
        pass

    def addFactions(self, factions):
        pass

    def addTradeRoutes(self, tradeRoutes):
        pass

    def updateTradeRoutes(self, tradeRoutes):
        pass

    def addCampaigns(self, campaigns):
        pass

    def makeGalacticPlot(self):
        return FakePlot()

    def emptyWidgets(self):
        pass

    def updateCampaignComboBox(self, campaigns, newCampaign):
        pass

    def updateCampaignComboBoxSelection(self, index):
        pass

    def updatePlanetComboBox(self, planets):
        self.combo_planets = planets

    def updatePlanetComboBoxSelection(self, planetName):
        self.selected_planet = planetName

    def getSelectedPlanetName(self):
        return self.selected_planet

    def updatePlanetSelection(self, planets):
        pass

    def updateTradeRouteSelection(self, tradeRoutes):
        pass

    def selectSingleTradeRoute(self, index):
        return True

    def updateFactionSelection(self, factions):
        pass

    def updatePlanetInfoDisplay(self, planet, startingForces, filter):
        pass

    def updatePlanetCountDisplay(self, planets):
        pass

    def updatePlanetMaxConnectionsCountDisplay(self, tradeRoutes):
        pass

    def updateTotalFactionIncome(self, entry):
        pass

    def clearPlanets(self):
        pass

    def clearTradeRoutes(self):
        pass


def test_planet_selection_filters_starting_forces_to_campaign_era_and_planets():
    repository = GameObjectRepository()
    alderaan = Planet("Alderaan")
    kuat = Planet("Kuat")
    campaign = Campaign("GC")
    campaign.eraStart = "2"
    repository.addPlanet(alderaan)
    repository.addPlanet(kuat)
    repository.addFaction(Faction("Empire"))
    repository.addFaction(Faction("Rebel"))
    repository.addFaction(Faction("Neutral"))
    repository.addCampaign(campaign)
    repository.startingForcesLibrary = pd.DataFrame(
        [
            ["Alderaan", 1, "Empire", "Garrison", 1],
            ["Alderaan", 2, "Rebel", "Garrison", 1],
            ["Kuat", 2, "Empire", "Garrison", 1],
        ],
        columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
    )
    presenter = MainWindowPresenter(FakeMainWindow(), repository, FakeConfig())

    presenter.onPlanetChecked(0, True)
    assert presenter.getSelectedCampaign().startingForces["Owner"].tolist() == [
        "Rebel"
    ]

    presenter.onPlanetChecked(1, True)
    assert set(presenter.getSelectedCampaign().startingForces["Planet"]) == {
        "Alderaan",
        "Kuat",
    }

    presenter.onPlanetChecked(0, False)
    assert presenter.getSelectedCampaign().startingForces["Planet"].tolist() == [
        "Kuat"
    ]


def test_gc_file_starting_forces_override_library_affiliation_for_that_planet():
    repository = GameObjectRepository()
    alderaan = Planet("Alderaan")
    kuat = Planet("Kuat")
    campaign = Campaign("GC")
    campaign.eraStart = "2"
    campaign.startingForces = pd.DataFrame(
        [["Alderaan", 0, "Empire", "File_Garrison", 1]],
        columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
    )
    repository.addPlanet(alderaan)
    repository.addPlanet(kuat)
    repository.addFaction(Faction("Empire"))
    repository.addFaction(Faction("Rebel"))
    repository.addFaction(Faction("Neutral"))
    repository.addCampaign(campaign)
    repository.startingForcesLibrary = pd.DataFrame(
        [
            ["Alderaan", 2, "Rebel", "Library_Garrison", 1],
            ["Kuat", 2, "Rebel", "Library_Garrison", 1],
        ],
        columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
    )

    presenter = MainWindowPresenter(FakeMainWindow(), repository, FakeConfig())
    presenter.onPlanetChecked(0, True)
    presenter.onPlanetChecked(1, True)

    forces = presenter.getSelectedCampaign().startingForces
    owners = dict(zip(forces["Planet"], forces["Owner"]))
    objects = dict(zip(forces["Planet"], forces["ObjectType"]))

    assert owners == {"Alderaan": "Empire", "Kuat": "Rebel"}
    assert objects["Alderaan"] == "File_Garrison"
    assert set(forces["Era"]) == {2}
