import pandas as pd
import pytest

from gameObjects.aiplayer import AIPlayer
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute


@pytest.fixture
def repo():
    return GameObjectRepository()


def make_route(name, start, end):
    route = TradeRoute(name)
    route.start = start
    route.end = end
    return route


def test_add_and_get_campaign_by_set_name(repo):
    campaign = Campaign("GC_1")
    campaign.setName = "Progressive"

    repo.addCampaign(campaign)

    found = repo.getCampaignBySetName("Progressive")
    assert found is campaign


def test_add_and_get_planet_by_name(repo):
    planet = Planet("Alderaan")
    repo.addPlanet(planet)

    assert repo.getPlanetByName("Alderaan") is planet


def test_add_and_get_faction_by_name(repo):
    faction = Faction("Empire")
    repo.addFaction(faction)

    assert repo.getFactionByName("Empire") is faction


def test_get_trade_route_by_planets_matches_both_directions(repo):
    p1 = Planet("Alderaan")
    p2 = Planet("Kuat")
    route = make_route("CorellianRun", p1, p2)
    repo.addTradeRoute(route)

    assert repo.getTradeRouteByPlanets(p1, p2) is route
    assert repo.getTradeRouteByPlanets(p2, p1) is route


def test_planet_exists_and_trade_route_exists(repo):
    p1 = Planet("Alderaan")
    p2 = Planet("Kuat")
    route = make_route("CorellianRun", p1, p2)

    repo.addPlanet(p1)
    repo.addPlanet(p2)
    repo.addTradeRoute(route)

    assert repo.planetExists("Alderaan") is True
    assert repo.planetExists("Bespin") is False
    assert repo.tradeRouteExists("Alderaan", "Kuat") is True
    assert repo.tradeRouteExists("Alderaan", "Bespin") is False


def test_getters_raise_runtime_error_when_missing(repo):
    with pytest.raises(RuntimeError, match="campaign set"):
        repo.getCampaignBySetName("MissingSet")

    with pytest.raises(RuntimeError, match="planet"):
        repo.getPlanetByName("MissingPlanet")

    with pytest.raises(RuntimeError, match="faction"):
        repo.getFactionByName("MissingFaction")

    p1 = Planet("Alderaan")
    p2 = Planet("Kuat")
    with pytest.raises(RuntimeError, match="Trade Route"):
        repo.getTradeRouteByPlanets(p1, p2)


def test_remove_methods_and_empty_repository(repo):
    campaign = Campaign("GC_1")
    campaign.setName = "Progressive"
    p1 = Planet("Alderaan")
    p2 = Planet("Kuat")
    route = make_route("CorellianRun", p1, p2)
    faction = Faction("Empire")
    aiplayer = AIPlayer("SandboxHuman")

    repo.addCampaign(campaign)
    repo.addPlanet(p1)
    repo.addPlanet(p2)
    repo.addTradeRoute(route)
    repo.addFaction(faction)
    repo.addAIPlayer(aiplayer)

    repo.removeCampaign(campaign)
    repo.removeTradeRoute(route)
    repo.removeFaction(faction)
    repo.removeAIPlayer(aiplayer)
    repo.removePlanet(p2)

    assert campaign not in repo.campaigns
    assert route not in repo.tradeRoutes
    assert faction not in repo.factions
    assert aiplayer not in repo.aiplayers
    assert p2 not in repo.planets

    repo.emptyRepository()
    assert len(repo.campaigns) == 0
    assert len(repo.planets) == 0
    assert len(repo.tradeRoutes) == 0
    assert len(repo.factions) == 0
    assert len(repo.aiplayers) == 0


def test_property_sets_are_returned_as_copies(repo):
    planet = Planet("Alderaan")
    repo.addPlanet(planet)

    external = repo.planets
    external.clear()

    # Repository should be unchanged because property returns a copy.
    assert repo.getPlanetByName("Alderaan") is planet


def test_get_planet_names_and_starting_forces_library(repo):
    p1 = Planet("Kuat")
    p2 = Planet("Alderaan")
    repo.addPlanet(p1)
    repo.addPlanet(p2)

    names = repo.getPlanetNames()
    assert set(names) == {"Alderaan", "Kuat"}

    df = pd.DataFrame([{"Planet": "Alderaan", "Owner": "Empire"}])
    repo.startingForcesLibrary = df
    assert repo.startingForcesLibrary.equals(df)

    # None should be accepted by the setter.
    repo.startingForcesLibrary = None
    assert repo.startingForcesLibrary is None
