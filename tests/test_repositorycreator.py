import lxml.etree as et

from RepositoryCreator import RepositoryCreator
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
