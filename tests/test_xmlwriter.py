import os

import lxml.etree as et
import pytest

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from xmlTools.xmlwriter import XMLWriter


@pytest.fixture
def writer():
    return XMLWriter()


def test_writer_writes_xml_file(writer, tmp_path):
    output_path = tmp_path / "Out.XML"
    tree = et.ElementTree(et.Element("Root"))

    writer.writer(tree, str(output_path))

    assert output_path.exists()
    root = et.parse(str(output_path)).getroot()
    assert root.tag == "Root"


def test_trade_route_writer_writes_routes_file(writer, tmp_path):
    old_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        p1 = Planet("Alderaan")
        p2 = Planet("Kuat")
        route = TradeRoute("CorellianRun")
        route.start = p1
        route.end = p2

        writer.tradeRouteWriter([route])

        output_path = tmp_path / "NewTradeRoutes.xml"
        assert output_path.exists()

        root = et.parse(str(output_path)).getroot()
        assert root.tag == "TradeRoutes"
        trade_route = root.find("TradeRoute")
        assert trade_route is not None
        assert trade_route.get("Name") == "CorellianRun"
        assert trade_route.find("Point_A").text == "Alderaan"
        assert trade_route.find("Point_B").text == "Kuat"
    finally:
        os.chdir(old_cwd)


def test_planet_coordinates_writer_updates_positions(writer, tmp_path):
        file_name = "Planets.XML"
        output_path = tmp_path / file_name

        root = et.Element("GameObjects")
        p1 = et.SubElement(root, "Planet", Name="Alderaan")
        gp1 = et.SubElement(p1, "Galactic_Position")
        gp1.text = "1.0, 2.0, 3.0"

        p2 = et.SubElement(root, "Planet", Name="Kuat")
        gp2 = et.SubElement(p2, "Galactic_Position")
        gp2.text = "4.0, 5.0, 6.0"

        tree = et.ElementTree(root)

        writer.planetCoordinatesWriter(
            str(tmp_path) + os.sep,
            {file_name: tree},
            {"Alderaan": [10.0, 20.0]},
        )

        written = et.parse(str(output_path)).getroot()
        alderaan = written.find(".//Planet[@Name='Alderaan']/Galactic_Position")
        kuat = written.find(".//Planet[@Name='Kuat']/Galactic_Position")

        assert alderaan.text == "10.0, 20.0, 3.0"
        assert kuat.text == "4.0, 5.0, 6.0"


def test_create_list_entry_sorts_by_name(writer):
    p1 = Planet("Kuat")
    p2 = Planet("Alderaan")

    entry = writer.createListEntry([p1, p2])

    assert "\n\t\t\tAlderaan,\n\t\t\tKuat,\n" in entry
