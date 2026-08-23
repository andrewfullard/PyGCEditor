import os
import pandas as pd
from PyQt6.QtWidgets import QApplication

import main
from config import Config
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


class EmptyRepositoryCreator:
    def constructRepository(self, data_folders, starting_forces_library_url):
        return GameObjectRepository()


def test_main_launches_with_dummy_data(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    def create_app(*args, **kwargs):
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    monkeypatch.setattr(main, "QApplication", create_app)
    monkeypatch.setattr(main, "RepositoryCreator", DummyRepositoryCreator)

    result = main.main(argv=["main.py"], start_event_loop=False)

    assert result == 0


def test_loading_log_dialog_hides_after_startup(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    dialogs = []

    class TestLoadingDialog:
        def __init__(self):
            dialogs.append(self)
            self.loading = False
            self.complete = False

        def beginLoading(self):
            self.loading = True

        def completeLoading(self):
            self.complete = True

        def updateProgress(self, description, current, total):
            pass

        def appendLogRecord(self, record):
            pass

    monkeypatch.setattr(main, "QApplication", lambda _: QApplication.instance() or QApplication([]))
    monkeypatch.setattr(main, "QtLoadingLogDialog", TestLoadingDialog)
    monkeypatch.setattr(main, "RepositoryCreator", DummyRepositoryCreator)

    result = main.main(argv=["main.py"], start_event_loop=False)

    assert result == 0
    assert dialogs[0].loading is True
    assert dialogs[0].complete is True


def test_show_loading_log_action_reopens_log_dialog(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    class TestLoadingDialog:
        def __init__(self):
            self.wasShown = False

        def showLog(self):
            self.wasShown = True

    window = QtMainWindow()
    dialog = TestLoadingDialog()
    window.setLoadingLogDialog(dialog)
    options_menu = next(
        action.menu()
        for action in window.getWindow().menuBar().actions()
        if action.text() == "Options"
    )
    show_log_action = next(
        action for action in options_menu.actions() if action.text() == "Show Loading Log"
    )

    show_log_action.trigger()

    assert dialog.wasShown is True
    window.getWindow().close()


def test_main_launches_with_no_campaigns(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    def create_app(*args, **kwargs):
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    monkeypatch.setattr(main, "QApplication", create_app)
    monkeypatch.setattr(main, "RepositoryCreator", EmptyRepositoryCreator)

    result = main.main(argv=["main.py"], start_event_loop=False)

    assert result == 0


def test_config_resolves_absolute_submod_paths(tmp_path, monkeypatch):
    absolute_submod = tmp_path / "ExternalSubmod"
    (tmp_path / "Data").mkdir()
    (absolute_submod / "Data").mkdir(parents=True)
    (tmp_path / "config.xml").write_text(
        f"""<Config>
    <ModPath>{tmp_path}</ModPath>
    <Submod>{absolute_submod}</Submod>
    <MaximumFleetMovementDistance>0</MaximumFleetMovementDistance>
    <StartingForcesLibraryURL></StartingForcesLibraryURL>
</Config>""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    config = Config()

    assert config.dataFolders == [
        os.path.join(str(tmp_path), "Data"),
        os.path.join(str(absolute_submod), "Data"),
    ]


def test_config_save_preserves_readable_xml_format(tmp_path, monkeypatch):
    (tmp_path / "config.xml").write_text(
        """<Config>
    <ModPath>C:\\Mods\\Base</ModPath>
    <!-- Submods -->
    <Submod>Old</Submod>
    <MaximumFleetMovementDistance>0</MaximumFleetMovementDistance>
    <StartingForcesLibraryURL>forces.csv</StartingForcesLibraryURL>
</Config>
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    config = Config()
    config.save("C:\\Mods\\Base", ["First", "Second"], 5, "forces.csv")

    assert (tmp_path / "config.xml").read_text(encoding="utf-8") == (
        """<?xml version='1.0' encoding='UTF-8'?>
<Config>
    <ModPath>C:\\Mods\\Base</ModPath>
    <!-- Submods -->
    <Submod>First</Submod>
    <Submod>Second</Submod>
    <MaximumFleetMovementDistance>5</MaximumFleetMovementDistance>
    <StartingForcesLibraryURL>forces.csv</StartingForcesLibraryURL>
</Config>
"""
    )


