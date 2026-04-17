import pandas as pd
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

import main
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute


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
