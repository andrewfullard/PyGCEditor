from types import SimpleNamespace

import pandas as pd

from export_campaign_planets_lua import (
    campaign_export_name,
    campaign_lua_table,
    export_campaigns,
)
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute


def test_campaign_lua_table_exports_owners_and_adjacency():
    coruscant = Planet("Coruscant")
    byss = Planet("BYSS")
    carida = Planet("CARIDA")

    route_a = TradeRoute("Coruscant_Byss")
    route_a.start = coruscant
    route_a.end = byss
    route_b = TradeRoute("Carida_Coruscant")
    route_b.start = carida
    route_b.end = coruscant

    campaign = Campaign("Test GC")
    campaign.eraStart = "1"
    campaign.planets = {coruscant, byss, carida}
    campaign.tradeRoutes = {route_a, route_b}
    campaign.startingForces = pd.DataFrame(
        [
            ["Coruscant", 1, "REBEL", "Unit", 1],
            ["BYSS", 1, "Empire", "Unit", 1],
        ],
        columns=["Planet", "Era", "Owner", "ObjectType", "Amount"],
    )

    assert campaign_lua_table(campaign) == (
        "return {\n"
        '    ["BYSS"] = { owner = "EMPIRE", adjacent = {"CORUSCANT"} },\n'
        '    ["CARIDA"] = { owner = "NEUTRAL", adjacent = {"CORUSCANT"} },\n'
        '    ["CORUSCANT"] = { owner = "REBEL", adjacent = {"BYSS", "CARIDA"} },\n'
        "}\n"
    )


def test_campaign_export_name_removes_playable_faction():
    campaign = Campaign("FullProgressive_Empire")
    campaign.setName = "FullProgressive"
    campaign.playableFactions = {Faction("Empire")}

    assert campaign_export_name(campaign) == "FULLPROGRESSIVE"


def test_campaign_export_name_keeps_faction_words_in_set_name():
    campaign = Campaign("Crimson_Empire")
    campaign.setName = "Crimson_Empire"
    campaign.playableFactions = {Faction("Empire")}

    assert campaign_export_name(campaign) == "CRIMSON_EMPIRE"


def test_different_layouts_export_one_file_per_campaign(tmp_path):
    empire = Campaign("FullProgressive_Empire")
    empire.setName = "FullProgressive"
    empire.differentLayoutPerFaction = True

    rebel = Campaign("FullProgressive_Rebel")
    rebel.setName = "FullProgressive"
    rebel.differentLayoutPerFaction = True

    export_campaigns(SimpleNamespace(campaigns={empire, rebel}), tmp_path)

    assert {path.name for path in tmp_path.iterdir()} == {
        "FULLPROGRESSIVE_EMPIRE.lua",
        "FULLPROGRESSIVE_REBEL.lua",
    }
