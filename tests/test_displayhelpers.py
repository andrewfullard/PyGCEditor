from DisplayHelpers import DisplayHelpers
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet


def test_calculate_faction_income_includes_planet_counts() -> None:
    repository = GameObjectRepository()
    helper = DisplayHelpers(repository, [Campaign("GC")])

    empire = Faction("Empire")
    neutral = Faction("Neutral")

    p1 = Planet("Alderaan")
    p1.income = 100
    p2 = Planet("Kuat")
    p2.income = 200
    p3 = Planet("Byss")
    p3.income = 50

    totals = helper.calculateFactionIncome(
        planets=[p1, p2, p3],
        planet_owners=[empire, empire, neutral],
    )

    assert totals["Empire"]["income"] == 300
    assert totals["Empire"]["planets"] == 2
    assert totals["Neutral"]["income"] == 50
    assert totals["Neutral"]["planets"] == 1


def test_calculate_faction_income_empty_returns_empty_dict() -> None:
    repository = GameObjectRepository()
    helper = DisplayHelpers(repository, [Campaign("GC")])

    totals = helper.calculateFactionIncome(planets=[], planet_owners=[])

    assert totals == {}
