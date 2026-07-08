import lxml.etree as et
import pandas as pd

from RepositoryCreator import RepositoryCreator
from gameObjects.campaign import Campaign
from gameObjects.faction import Faction
from gameObjects.planet import Planet


def test_add_trade_routes_skips_malformed_entries() -> None:
    creator = RepositoryCreator()
    creator.repository.addPlanet(Planet("Alderaan"))
    creator.repository.addPlanet(Planet("Kuat"))

    trade_route_root = et.fromstring(
        """<?xml version='1.0'?>
<TradeRoutes>
    <TradeRoute Name='CorellianRun'>
        <Point_A>Alderaan</Point_A>
        <Point_B>Kuat</Point_B>
    </TradeRoute>
    <TradeRoute Name='BrokenRoute'>
        <Point_A>Alderaan</Point_A>
        <Point_B>UnknownPlanet</Point_B>
    </TradeRoute>
</TradeRoutes>
"""
    )

    creator.addTradeRoutesFromXML([trade_route_root])

    route_names = {route.name for route in creator.repository.tradeRoutes}
    assert route_names == {"CorellianRun"}

    loaded_route = next(iter(creator.repository.tradeRoutes))
    assert loaded_route.start.name == "Alderaan"
    assert loaded_route.end.name == "Kuat"


def test_get_starting_forces_library_returns_none_when_file_missing() -> None:
    creator = RepositoryCreator()

    result = creator.getStartingForcesLibrary("this-file-does-not-exist.csv")

    assert result is None


def test_get_starting_forces_library_returns_none_when_file_malformed(tmp_path) -> None:
    creator = RepositoryCreator()
    malformed_csv = tmp_path / "malformed.csv"
    # Missing required columns such as Era/Owner/ObjectType/Amount/ReuseEra.
    pd.DataFrame([{"Planet": "Alderaan"}]).to_csv(malformed_csv, index=False)

    result = creator.getStartingForcesLibrary(str(malformed_csv))

    assert result is None


def test_add_campaigns_folds_existing_ccogm_alternate_into_base_campaign() -> None:
    creator = RepositoryCreator()
    creator.repository.addFaction(Faction("Empire"))
    for planet_name in ("Coruscant", "Kessel", "Thyferra"):
        creator.repository.addPlanet(Planet(planet_name))

    base = et.fromstring(
        """
<Campaign Name="FullMedium_Era_2_Empire">
    <Campaign_Set>FullMedium_Era_2</Campaign_Set>
    <Starting_Active_Player>Empire</Starting_Active_Player>
    <Locations>Coruscant, Kessel, Thyferra</Locations>
    <Starting_Forces>Empire, Coruscant, Generate_Force</Starting_Forces>
    <Starting_Forces>Warlords, Kessel, Generate_Force</Starting_Forces>
    <Starting_Forces>Empire, Thyferra, Generate_Force</Starting_Forces>
</Campaign>
"""
    )
    alternate = et.fromstring(
        """
<Campaign Name="FullMedium_Era_2_Empire_CCoGM">
    <Campaign_Set>FullMedium_Era_2_CCoGM</Campaign_Set>
    <Starting_Active_Player>Empire</Starting_Active_Player>
    <Locations>Coruscant, Kessel, Thyferra</Locations>
    <Starting_Forces>Empire, Coruscant, Generate_Force</Starting_Forces>
    <Starting_Forces>Empire, Coruscant, CCoGM_Dummy</Starting_Forces>
    <Starting_Forces>Empire, Kessel, Generate_Force</Starting_Forces>
    <Starting_Forces>Warlords, Thyferra, Generate_Force</Starting_Forces>
</Campaign>
"""
    )

    creator.addCampaignsFromXML(
        [
            ("FullMedium_Era_2.XML", "FullMedium_Era_2_Empire", base),
            (
                "FullMedium_Era_2.XML",
                "FullMedium_Era_2_Empire_CCoGM",
                alternate,
            ),
        ]
    )

    campaigns = creator.repository.campaigns
    campaign = creator.repository.getCampaignBySetName("FullMedium_Era_2")

    assert len(campaigns) == 1
    assert campaign.alternateSets == [
        {
            "enabled": True,
            "suffix": "CCoGM",
            "faction": "Empire",
            "dummy_planet": "Coruscant",
            "planet_affiliations": {
                "Kessel": "Empire",
                "Thyferra": "Warlords",
            },
        }
    ]


def test_construct_repository_keeps_campaigns_when_starting_forces_library_missing(
    monkeypatch,
) -> None:
    creator = RepositoryCreator()
    campaign = Campaign("TestCampaign")

    def fake_exists(path):
        return path.endswith("CampaignFiles.XML")

    def fake_find_meta_with_paths(_campaign_file, _folders):
        return []

    def fake_add_campaigns(_entries):
        creator.repository.addCampaign(campaign)

    monkeypatch.setattr("RepositoryCreator.os.path.exists", fake_exists)
    monkeypatch.setattr(
        creator._RepositoryCreator__xml,
        "findMetaFileRefsWithPaths",
        fake_find_meta_with_paths,
    )
    monkeypatch.setattr(creator, "addCampaignsFromXML", fake_add_campaigns)

    repository = creator.constructRepository(["C:/fake/Data"], "missing.csv")

    assert campaign in repository.campaigns
    assert repository.startingForcesLibrary is None
