from types import SimpleNamespace

from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from ui.qtmainwindow import QtMainWindow


from PyQt6.QtWidgets import QApplication


def test_dark_map_changes_map_colors_only(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    axes = plot._QtGalacticPlot__axes

    plot.setDarkMode(True)
    assert axes.get_facecolor()[:3] == (32 / 255, 33 / 255, 36 / 255)

    plot.setDarkMode(False)
    assert axes.get_facecolor()[:3] == (1.0, 1.0, 1.0)

    window.getWindow().close()


def test_planet_hover_shows_subtle_possible_trade_routes(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    selected_planet = Planet("Alderaan")
    selected_planet.x = 10.0
    selected_planet.y = 10.0
    other_planet = Planet("Kuat")
    other_planet.x = 20.0
    other_planet.y = 20.0
    route = TradeRoute("CorellianRun")
    route.start = selected_planet
    route.end = other_planet

    plot.plotGalaxy(
        planets=[selected_planet],
        tradeRoutes=[],
        allPlanets=[selected_planet, other_planet],
        planetOwners=[],
        allTradeRoutes=[route],
    )
    plot._QtGalacticPlot__show_trade_route_preview(0)

    preview_line = plot._QtGalacticPlot__tradeRoutePreviewLines[0]
    assert preview_line.get_alpha() == 0.25
    assert preview_line.get_linestyle() == "--"

    window.getWindow().close()


def test_map_supports_scroll_zoom_and_middle_mouse_pan(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    planet_a = Planet("Alderaan")
    planet_a.x = 10.0
    planet_a.y = 10.0
    planet_b = Planet("Kuat")
    planet_b.x = 20.0
    planet_b.y = 20.0
    plot.plotGalaxy([], [], [planet_a, planet_b], [])
    axes = plot._QtGalacticPlot__axes

    plot._QtGalacticPlot__zoomPlot(
        SimpleNamespace(inaxes=axes, xdata=15.0, ydata=15.0, step=1)
    )
    assert axes.get_xlim() == (11.0, 19.0)
    assert axes.get_ylim() == (11.0, 19.0)

    plot._QtGalacticPlot__startPan(
        SimpleNamespace(inaxes=axes, xdata=15.0, ydata=15.0, button=2)
    )
    plot._QtGalacticPlot__panPlot(
        SimpleNamespace(xdata=16.0, ydata=17.0)
    )
    assert axes.get_xlim() == (10.0, 18.0)
    assert axes.get_ylim() == (9.0, 17.0)
    plot._QtGalacticPlot__endPan(SimpleNamespace(button=2))

    plot.plotGalaxy([], [], [planet_a, planet_b], [])

    plot._QtGalacticPlot__galacticPlotNavBar.home()
    assert axes.get_xlim() == (10.0, 20.0)
    assert axes.get_ylim() == (10.0, 20.0)

    window.getWindow().close()


def test_middle_click_does_not_select_planet(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    selected_planets = []
    plot.planetSelectedSignal.connect(selected_planets.append)

    plot._QtGalacticPlot__planetSelect(
        SimpleNamespace(ind=[0], mouseevent=SimpleNamespace(button=2))
    )

    assert selected_planets == []
    window.getWindow().close()


def test_inactive_planet_cannot_start_trade_route_creation(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    active_planet = Planet("Alderaan")
    inactive_planet = Planet("Kuat")
    plot.plotGalaxy(
        planets=[active_planet],
        tradeRoutes=[],
        allPlanets=[active_planet, inactive_planet],
        planetOwners=[],
    )
    route_starts = []
    plot.planetShiftSelectedSignal.connect(route_starts.append)

    plot._QtGalacticPlot__planetSelect(
        SimpleNamespace(ind=[1], mouseevent=SimpleNamespace(button=3))
    )

    assert route_starts == []
    window.getWindow().close()


def test_show_planet_names_toggles_selected_planet_labels(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QtMainWindow()
    plot = window.makeGalacticPlot()
    planet = Planet("Alderaan")
    planet.x = 10.0
    planet.y = 10.0
    plot.plotGalaxy([planet], [], [planet], [])

    plot.setShowPlanetNames(True)
    assert [label.get_text() for label in plot._QtGalacticPlot__planetLabels] == [
        "Alderaan"
    ]
    assert plot._QtGalacticPlot__planetLabels[0].get_clip_on() is True

    plot.setDarkMode(True)
    assert plot._QtGalacticPlot__planetLabels[0].get_color() == "#f1f3f4"

    plot.setShowPlanetNames(False)
    assert plot._QtGalacticPlot__planetLabels == []
    window.getWindow().close()