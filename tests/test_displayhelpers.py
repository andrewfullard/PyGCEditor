import pandas as pd

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


def test_get_planet_owners_uses_campaign_starting_era() -> None:
    repository = GameObjectRepository()
    empire = Faction("Empire")
    rebel = Faction("Rebel")
    neutral = Faction("Neutral")
    planet = Planet("Alderaan")
    campaign = Campaign("GC")
    campaign.eraStart = "2"
    campaign.startingForces = pd.DataFrame(
        [
            ["Alderaan", 1, "Empire", "Garrison", 1],
            ["Alderaan", 2, "Rebel", "Garrison", 1],
        ],
        columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
    )

    repository.addFaction(empire)
    repository.addFaction(rebel)
    repository.addFaction(neutral)

    owners = DisplayHelpers(repository, [campaign]).getPlanetOwners(0, {planet})

    assert owners == [rebel]
