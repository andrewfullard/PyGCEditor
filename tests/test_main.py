import pandas as pd
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

import main
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from ui.qtmainwindow import QtMainWindow


def _build_dummy_repository() -> GameObjectRepository:
    repository = GameObjectRepository()

    planet_a = Planet("Alderaan")
    planet_a.x = 10.0
    planet_a.y = 10.0
    planet_a.income = 100

    planet_b = Planet("Kuat")
    planet_b.x = 20.0
    planet_b.y = 20.0
    planet_b.income = 200

    empire = Faction("Empire")
    neutral = Faction("Neutral")

    route = TradeRoute("CorellianRun")
    route.start = planet_a
    route.end = planet_b

    campaign = Campaign("TestCampaign")
    campaign.setName = "TestCampaign"
    campaign.planets = {planet_a, planet_b}
    campaign.tradeRoutes = {route}
    campaign.playableFactions = {empire}
    campaign.startingForces = pd.DataFrame(
        [[planet_a.name, 1, empire.name, "Stormtrooper_Squad", 1]],
        columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
    )

    repository.addPlanet(planet_a)
    repository.addPlanet(planet_b)
    repository.addFaction(empire)
    repository.addFaction(neutral)
    repository.addTradeRoute(route)
    repository.addCampaign(campaign)
    repository.startingForcesLibrary = campaign.startingForces.copy()

    return repository


class DummyRepositoryCreator:
    def __init__(self):
        self.repository = _build_dummy_repository()

    def constructRepository(self, data_folders, starting_forces_library_url):
        return self.repository


def test_main_launches_with_dummy_data(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    def create_app(*args, **kwargs):
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Run one event-loop cycle and quit, so startup wiring executes.
        QTimer.singleShot(0, app.quit)
        return app

    monkeypatch.setattr(main, "QApplication", create_app)
    monkeypatch.setattr(main, "RepositoryCreator", DummyRepositoryCreator)

    result = main.main(argv=["main.py"], start_event_loop=True)

    assert result == 0


def test_dark_map_action_changes_map_colors_only(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    options_menu = next(
        action.menu()
        for action in window.getWindow().menuBar().actions()
        if action.text() == "Options"
    )
    dark_map_action = next(
        action for action in options_menu.actions() if action.text() == "Dark Map"
    )
    axes = plot._QtGalacticPlot__axes

    dark_map_action.trigger()
    assert axes.get_facecolor()[:3] == (32 / 255, 33 / 255, 36 / 255)

    dark_map_action.trigger()
    assert axes.get_facecolor()[:3] == (1.0, 1.0, 1.0)

    window.getWindow().close()


def test_inactive_planet_hover_shows_subtle_possible_trade_routes(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    inactive_planet = Planet("Alderaan")
    inactive_planet.x = 10.0
    inactive_planet.y = 10.0
    other_planet = Planet("Kuat")
    other_planet.x = 20.0
    other_planet.y = 20.0
    route = TradeRoute("CorellianRun")
    route.start = inactive_planet
    route.end = other_planet

    plot.plotGalaxy(
        planets=[],
        tradeRoutes=[],
        allPlanets=[inactive_planet, other_planet],
        planetOwners=[],
        allTradeRoutes=[route],
    )
    plot._QtGalacticPlot__show_inactive_trade_routes(0)

    preview_line = plot._QtGalacticPlot__inactiveTradeRouteLines[0]
    assert preview_line.get_alpha() == 0.25
    assert preview_line.get_linestyle() == "--"

    window.getWindow().close()
