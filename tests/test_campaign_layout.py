import lxml.etree as et

from RepositoryCreator import RepositoryCreator
from gameObjects.faction import Faction
from gameObjects.planet import Planet


def test_different_layout_per_faction_is_loaded_from_xml():
    creator = RepositoryCreator()
    campaign_root = et.fromstring(
        """<Campaign Name="TestCampaign">
            <Campaign_Set>TestSet</Campaign_Set>
            <Starting_Active_Player> </Starting_Active_Player>
            <Locations> </Locations>
            <Sort_Order>0</Sort_Order>
            <Text_ID>TEST</Text_ID>
            <Description_Text>Test</Description_Text>
            <Era_Start>1</Era_Start>
            <Use_Default_Forces>False</Use_Default_Forces>
            <Rebel_Story_Name />
            <Empire_Story_Name />
            <Underworld_Story_Name />
            <Story_Name />
            <Is_Listed>True</Is_Listed>
            <Different_Layout_Per_Faction>True</Different_Layout_Per_Faction>
            <Trade_Routes> </Trade_Routes>
        </Campaign>"""
    )

    creator.addCampaignsFromXML(
        [("Campaign.xml", "TestCampaign", campaign_root)]
    )

    campaign = next(iter(creator.repository.campaigns))
    assert campaign.differentLayoutPerFaction is True


def test_same_faction_alternate_setup_is_loaded():
    creator = RepositoryCreator()
    creator.repository.addFaction(Faction("Empire"))
    creator.repository.addPlanet(Planet("Kessel"))

    base = _campaign_xml("GC", "Empire")
    alternate = _campaign_xml("GC_Alt", "Rebel")
    creator.addCampaignsFromXML(
        [
            ("Campaign.xml", "GC_Empire", base),
            ("Campaign.xml", "GC_Empire_Alt", alternate),
        ]
    )

    campaign = next(iter(creator.repository.campaigns))
    assert len(creator.repository.campaigns) == 1
    assert campaign.alternateSets == [
        {
            "enabled": True,
            "suffix": "Alt",
            "faction": "Empire",
            "dummy_planet": "",
            "planet_affiliations": {"Kessel": "Rebel"},
        }
    ]


def test_different_faction_layouts_are_loaded_as_separate_campaigns():
    creator = RepositoryCreator()
    creator.repository.addFaction(Faction("Empire"))
    creator.repository.addPlanet(Planet("Kessel"))

    empire = _campaign_xml("GC", "Empire", "Empire", different_layout=True)
    rebel = _campaign_xml("GC", "Rebel", "Rebel", different_layout=True)
    creator.repository.addFaction(Faction("Rebel"))
    creator.addCampaignsFromXML(
        [
            ("Campaign.xml", "GC_Empire", empire),
            ("Campaign.xml", "GC_Rebel", rebel),
        ]
    )

    assert {campaign.name for campaign in creator.repository.campaigns} == {
        "GC_Empire",
        "GC_Rebel",
    }


def _campaign_xml(
    set_name, owner, active_player="Empire", different_layout=False
):
    different_layout_tag = (
        "<Different_Layout_Per_Faction>True</Different_Layout_Per_Faction>"
        if different_layout
        else ""
    )
    return et.fromstring(
        f"""<Campaign>
            <Campaign_Set>{set_name}</Campaign_Set>
            <Starting_Active_Player>{active_player}</Starting_Active_Player>
            <Locations>Kessel</Locations>
            <Sort_Order>0</Sort_Order>
            <Text_ID>TEST</Text_ID>
            <Description_Text>Test</Description_Text>
            <Era_Start>1</Era_Start>
            <Use_Default_Forces>False</Use_Default_Forces>
            <Rebel_Story_Name />
            <Empire_Story_Name />
            <Underworld_Story_Name />
            <Story_Name />
            <Is_Listed>True</Is_Listed>
            {different_layout_tag}
            <Trade_Routes> </Trade_Routes>
            <Starting_Forces>{owner}, Kessel, Mine</Starting_Forces>
        </Campaign>"""
    )
