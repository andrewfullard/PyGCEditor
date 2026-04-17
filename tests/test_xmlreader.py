import lxml.etree as et
import pytest

from gameObjects.planet import Planet
from xmlTools.xmlreader import XMLReader
from xmlTools.xmlstructure import XMLStructure


@pytest.fixture
def reader():
    return XMLReader()


@pytest.fixture
def xml_workspace(tmp_path):
    data_dir = tmp_path / "Data"
    xml_dir = data_dir / "XML"
    xml_dir.mkdir(parents=True)
    XMLStructure.dataFolder = str(data_dir)

    def _write_xml(relative_path, xml_text):
        path = xml_dir / relative_path
        path.write_text(xml_text, encoding="utf-8")
        return str(path)

    return _write_xml


def test_parse_meta_and_find_planets_files(reader, xml_workspace):
    game_objects_meta = xml_workspace(
        "GameObjectFiles.XML",
        """<?xml version='1.0'?>
<GameObjectFiles>
    <File>Planets.XML</File>
    <File>Units.XML</File>
    <File>Missing.XML</File>
</GameObjectFiles>
""",
    )

    xml_workspace(
        "Planets.XML",
        """<?xml version='1.0'?>
<GameObjects>
    <Planet Name='Alderaan'>
        <Galactic_Position>1.0, 2.0, 0.0</Galactic_Position>
    </Planet>
</GameObjects>
""",
    )

    xml_workspace(
        "Units.XML",
        """<?xml version='1.0'?>
<GameObjects>
    <GroundCompany Name='Stormtrooper_Squad'>
        <AI_Combat_Power>12</AI_Combat_Power>
    </GroundCompany>
</GameObjects>
""",
    )

    meta_root = et.parse(game_objects_meta).getroot()
    assert reader.isMetaFile(meta_root)
    assert reader.parseMetaFile(meta_root) == [
        "Planets.XML",
        "Units.XML",
        "Missing.XML",
    ]

    planets_files = reader.findPlanetsFiles(game_objects_meta)
    assert len(planets_files) == 1
    assert planets_files[0].tag == "GameObjects"
    assert planets_files[0].find("Planet") is not None


def test_find_planet_files_and_roots_returns_planet_only(reader, xml_workspace):
    game_objects_meta = xml_workspace(
        "GameObjectFiles.XML",
        """<?xml version='1.0'?>
<GameObjectFiles>
    <File>Planets.XML</File>
    <File>Units.XML</File>
</GameObjectFiles>
""",
    )

    xml_workspace(
        "Planets.XML",
        """<?xml version='1.0'?>
<GameObjects>
    <Planet Name='Kuat'>
        <Galactic_Position>3.0, 4.0, 0.0</Galactic_Position>
    </Planet>
</GameObjects>
""",
    )

    xml_workspace(
        "Units.XML",
        """<?xml version='1.0'?>
<GameObjects>
    <GroundCompany Name='AT_AT'>
        <AI_Combat_Power>50</AI_Combat_Power>
    </GroundCompany>
</GameObjects>
""",
    )

    roots = reader.findPlanetFilesAndRoots(game_objects_meta)
    assert set(roots.keys()) == {"Planets.XML"}


def test_find_meta_file_refs_and_get_start_end(reader, xml_workspace):
    trade_meta = xml_workspace(
        "TradeRouteFiles.XML",
        """<?xml version='1.0'?>
<TradeRouteFiles>
    <File>Routes.XML</File>
    <File>MissingRoutes.XML</File>
</TradeRouteFiles>
""",
    )

    routes_file = xml_workspace(
        "Routes.XML",
        """<?xml version='1.0'?>
<TradeRoutes>
    <TradeRoute Name='CorellianRun'>
        <Point_A>Alderaan</Point_A>
        <Point_B>Kuat</Point_B>
    </TradeRoute>
</TradeRoutes>
""",
    )

    refs = reader.findMetaFileRefs(trade_meta)
    assert len(refs) == 1
    assert refs[0].tag == "TradeRoutes"

    route_root = et.parse(routes_file).getroot()
    p1 = Planet("Alderaan")
    p2 = Planet("Kuat")
    start, end = reader.getStartEnd("CorellianRun", {p1, p2}, route_root)
    assert start.name == "Alderaan"
    assert end.name == "Kuat"


def test_get_location_returns_xy(reader, xml_workspace):
    planet_file = xml_workspace(
        "Planets.XML",
        """<?xml version='1.0'?>
<GameObjects>
    <Planet Name='Bespin'>
        <Galactic_Position>10.5, 20.5, 7.0</Galactic_Position>
    </Planet>
</GameObjects>
""",
    )

    root = et.parse(planet_file).getroot()
    x, y = reader.getLocation("Bespin", root)
    assert x == 10.5
    assert y == 20.5
