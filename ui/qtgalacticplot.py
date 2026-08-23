from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal
from matplotlib.backends.backend_qtagg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Axes, Figure


class QtGalacticPlot(QWidget):
    """Class for plotting the galaxy"""

    # signal to send to main window presenter when a planet is selected in the plot
    planetSelectedSignal = pyqtSignal(int)
    planetShiftSelectedSignal = pyqtSignal(int)

    def __init__(self, parent: QWidget):
        super(QtGalacticPlot, self).__init__()
        self.__galacticPlotWidget: QWidget = QWidget(parent)
        self.__galacticPlotWidget.setLayout(QVBoxLayout())
        self.__is_first_run = True

        self.__galacticPlotCanvas: FigureCanvas = FigureCanvas(Figure())

        self.__galacticPlotCanvas.mpl_connect("pick_event", self.__planetSelect)
        self.__galacticPlotCanvas.mpl_connect("motion_notify_event", self.__planetHover)
        self.__galacticPlotCanvas.mpl_connect("scroll_event", self.__zoomPlot)
        self.__galacticPlotCanvas.mpl_connect("button_press_event", self.__startPan)
        self.__galacticPlotCanvas.mpl_connect("motion_notify_event", self.__panPlot)
        self.__galacticPlotCanvas.mpl_connect("button_release_event", self.__endPan)

        self.__galacticPlotNavBar: NavigationToolbar = NavigationToolbar(
            self.__galacticPlotCanvas, self.__galacticPlotWidget
        )
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotNavBar)
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotCanvas)
        self.__axes: Axes = self.__galacticPlotCanvas.figure.add_subplot(
            111, aspect="equal"
        )
        self.__backgroundColor = "#ffffff"
        self.__foregroundColor = "#202124"
        self.__routeColor = "k"
        self.__planetOutlineColor = "black"

        self.__annotate = self.__axes.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
            zorder=9,
        )
        self.__annotate.set_visible(False)
        self.__applyMapColors()
        self.__planetNames = []
        self.__planetOwners = []
        self.__starbaseLevel = []
        self.__shipyardLevel = []
        self.__SupportsStructure = []
        self.__income = []
        self.__groundStructureSlots = []
        self.__planetsScatter = None
        self.__tradeRouteTraceStart = None
        self.__tradeRouteTrace = []
        self.__tradeRouteLines = []
        self.__tradeRouteConnections = []
        self.__tradeRoutePreviewLines = []
        self.__allTradeRoutes = []
        self.__selectedPlanetNames = set()
        self.__panStart = None
        self.__isPanning = False
        self.__highlightedPlanetIndex = None

    def plotGalaxy(
        self,
        planets,
        tradeRoutes,
        allPlanets,
        planetOwners,
        autoPlanetConnectionDistance: int = 0,
        allTradeRoutes=None,
    ) -> None:
        """Plots all planets as alpha = 0.1, then overlays all selected planets and trade routes"""
        if not allPlanets:
            self.__axes.clear()
            self.__applyMapColors()
            self.__galacticPlotCanvas.draw_idle()
            return

        if self.__is_first_run:
            x = [p.x for p in allPlanets]
            y = [p.y for p in allPlanets]
            self.__axes.set_xlim(min(x), max(x))
            self.__axes.set_ylim(min(y), max(y))

        self.__is_first_run = False

        xlim = self.__axes.get_xlim()
        ylim = self.__axes.get_ylim()
        self.__axes.autoscale(False)
        self.__axes.clear()
        self.__axes.set_xlim(xlim)
        self.__axes.set_ylim(ylim)
        self.__applyMapColors()
        self.__allTradeRoutes = allTradeRoutes or []
        self.__selectedPlanetNames = {planet.name for planet in planets}

        # Has to be set again here for the planet hover labels to work
        self.__annotate = self.__axes.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
            zorder=9,
        )
        self.__annotate.set_visible(False)
        self.__tradeRouteTrace = self.__axes.plot(
            [0, 0], [0, 0], color=self.__routeColor
        )
        self.__tradeRouteLines = []
        self.__tradeRouteConnections = []
        self.__tradeRoutePreviewLines = []
        self.__highlightedPlanetIndex = None

        self.__planetNames = []
        self.__planetOwners = []
        self.__starbaseLevel = []
        self.__shipyardLevel = []
        self.__SupportsStructure = []
        self.__income = []
        self.__groundStructureSlots = []

        x = []
        y = []

        for ap in allPlanets:
            found_pa = False
            for pa, po in zip(planets, planetOwners):
                if ap.name == pa.name:
                    self.__planetOwners.append(po.name)
                    found_pa = True
            if not found_pa:
                self.__planetOwners.append("N/A")

        for p in allPlanets:
            x.append(p.x)
            y.append(p.y)
            self.__planetNames.append(p.name)
            self.__starbaseLevel.append(p.starbaseLevel)
            self.__shipyardLevel.append(p.shipyardLevel)
            self.__income.append(p.income)
            self.__SupportsStructure.append(p.SupportsStructure)
            self.__groundStructureSlots.append(p.groundStructureSlots)

        self.__planetsScatter = self.__axes.scatter(
            x,
            y,
            c="grey",
            alpha=0.1,
            edgecolors=self.__planetOutlineColor,
            picker=5,
            zorder=2,
        )

        # loop through routes
        for t in tradeRoutes:
            route_line = self.__plot_trade_route(t, alpha=0.4, zorder=1)
            self.__tradeRouteLines.append(route_line)
            self.__tradeRouteConnections.append((t.start.name, t.end.name))

        # Create automatic connections between planets
        if autoPlanetConnectionDistance > 0:
            for p1 in planets:
                for p2 in planets:
                    if p1 == p2:
                        break
                    dist: float = p1.distanceTo(p2)
                    if dist < autoPlanetConnectionDistance:
                        self.__axes.plot(
                            [p1.x, p2.x],
                            [p1.y, p2.y],
                            color=self.__routeColor,
                            alpha=0.1,
                            zorder=1,
                        )

        x = []
        y = []

        if planetOwners:
            color = []
            for p, f in zip(planets, planetOwners):
                x.append(p.x)
                y.append(p.y)
                if f and f.color:
                    color.append(tuple(f.color))
                else:
                    color.append((0, 0, 0))

            self.__axes.scatter(
                x, y, c=color, edgecolors=self.__planetOutlineColor, zorder=4
            )
        else:
            for p in planets:
                x.append(p.x)
                y.append(p.y)

            self.__axes.scatter(x, y, c="grey", zorder=3)

        self.__galacticPlotNavBar.update()
        self.__galacticPlotNavBar.push_current()
        self.__galacticPlotCanvas.draw_idle()

    def getWidget(self) -> QWidget:
        """Returns the plot widget"""
        return self.__galacticPlotWidget

    def setDarkMode(self, enabled: bool) -> None:
        """Set the map colors without changing planet faction colors."""
        if enabled:
            self.__backgroundColor = "#202124"
            self.__foregroundColor = "#f1f3f4"
            self.__routeColor = "#d9e2ec"
            self.__planetOutlineColor = "#f1f3f4"
        else:
            self.__backgroundColor = "#ffffff"
            self.__foregroundColor = "#202124"
            self.__routeColor = "k"
            self.__planetOutlineColor = "black"

        self.__applyMapColors()
        self.__galacticPlotCanvas.draw_idle()

    def __applyMapColors(self) -> None:
        self.__galacticPlotCanvas.figure.set_facecolor(self.__backgroundColor)
        self.__axes.set_facecolor(self.__backgroundColor)
        self.__axes.tick_params(colors=self.__foregroundColor)
        for spine in self.__axes.spines.values():
            spine.set_color(self.__foregroundColor)
        self.__annotate.get_bbox_patch().set_facecolor(self.__backgroundColor)
        self.__annotate.get_bbox_patch().set_edgecolor(self.__foregroundColor)
        self.__annotate.set_color(self.__foregroundColor)

    def __planetSelect(self, event) -> None:
        """Event handler for selecting a planet on the map"""
        planet_index = event.ind[0]
        if event.mouseevent.button == 3:
            if self.__planetNames[planet_index] not in self.__selectedPlanetNames:
                return
            self.planetShiftSelectedSignal.emit(planet_index)
        elif event.mouseevent.button == 1:
            self.planetSelectedSignal.emit(planet_index)

    def __zoomPlot(self, event) -> None:
        """Zoom the map around the cursor position with the scroll wheel."""
        if event.inaxes != self.__axes or event.xdata is None or event.ydata is None:
            return

        zoom_factor = 0.8 if event.step > 0 else 1.25
        xlim = self.__axes.get_xlim()
        ylim = self.__axes.get_ylim()
        self.__axes.set_xlim(
            event.xdata + (xlim[0] - event.xdata) * zoom_factor,
            event.xdata + (xlim[1] - event.xdata) * zoom_factor,
        )
        self.__axes.set_ylim(
            event.ydata + (ylim[0] - event.ydata) * zoom_factor,
            event.ydata + (ylim[1] - event.ydata) * zoom_factor,
        )
        self.__galacticPlotNavBar.push_current()
        self.__galacticPlotCanvas.draw_idle()

    def __startPan(self, event) -> None:
        """Begin panning when the middle mouse button is pressed."""
        if event.button == 2 and event.inaxes == self.__axes:
            self.__panStart = (
                event.xdata,
                event.ydata,
                self.__axes.get_xlim(),
                self.__axes.get_ylim(),
            )
            self.__isPanning = False

    def __panPlot(self, event) -> None:
        """Move the map while the middle mouse button is held and dragged."""
        if self.__panStart is None or event.xdata is None or event.ydata is None:
            return

        start_x, start_y, xlim, ylim = self.__panStart
        delta_x = start_x - event.xdata
        delta_y = start_y - event.ydata
        self.__axes.set_xlim(xlim[0] + delta_x, xlim[1] + delta_x)
        self.__axes.set_ylim(ylim[0] + delta_y, ylim[1] + delta_y)
        self.__isPanning = True
        self.__galacticPlotCanvas.draw_idle()

    def __endPan(self, event) -> None:
        """End panning when the middle mouse button is released."""
        if event.button == 2:
            if self.__isPanning:
                self.__galacticPlotNavBar.push_current()
            self.__panStart = None
            self.__isPanning = False

    def __planetHover(self, event) -> None:
        """Handler for hovering on a planet in the plot"""
        visible = self.__annotate.get_visible()

        if event.inaxes == self.__axes:
            """Remove previous tradeRouteTrace lines if they exist"""
            for line in self.__tradeRouteTrace:
                line.remove()

            """Add tracing lines when drawing Trade Routes"""
            if self.__tradeRouteTraceStart is not None:
                startpos = self.__planetsScatter.get_offsets()[
                    self.__tradeRouteTraceStart
                ]
                self.__tradeRouteTrace = self.__axes.plot(
                    [startpos[0], event.xdata],
                    [startpos[1], event.ydata],
                    color="y",
                    lw=0.8,
                    ls="--",
                )
            else:
                self.__tradeRouteTrace = self.__axes.plot(
                    [0, 0], [0, 0], color=self.__routeColor
                )

            """Display annotation tooltip if the cursor is over a planet"""
            if self.__planetsScatter:
                contains, ind = self.__planetsScatter.contains(event)
            else:
                contains = False

            if contains:
                hovered_planet_index = ind["ind"][0]
                if self.__highlightedPlanetIndex != hovered_planet_index:
                    self.__reset_trade_route_highlight()
                    self.__remove_trade_route_preview()
                    self.__show_trade_route_preview(hovered_planet_index)
                    self.__highlightedPlanetIndex = hovered_planet_index
                self.__update_annotation(ind)
                self.__annotate.set_visible(True)
            else:
                if self.__highlightedPlanetIndex is not None:
                    self.__reset_trade_route_highlight()
                    self.__remove_trade_route_preview()
                    self.__highlightedPlanetIndex = None
                if visible:
                    self.__annotate.set_visible(False)

            self.__galacticPlotCanvas.draw_idle()
        else:
            if self.__highlightedPlanetIndex is not None:
                self.__reset_trade_route_highlight()
                self.__remove_trade_route_preview()
                self.__highlightedPlanetIndex = None
                self.__galacticPlotCanvas.draw_idle()

    def __reset_trade_route_highlight(self) -> None:
        """Restore default styling for all trade routes."""
        for line in self.__tradeRouteLines:
            line.set_color(self.__routeColor)
            line.set_alpha(0.4)
            line.set_linewidth(1.0)
            line.set_zorder(1)

    def __remove_trade_route_preview(self) -> None:
        for line in self.__tradeRoutePreviewLines:
            line.remove()
        self.__tradeRoutePreviewLines = []

    def __show_trade_route_preview(self, planet_index: int) -> None:
        """Show subtle previews for routes available from the hovered planet."""
        if planet_index < 0 or planet_index >= len(self.__planetNames):
            return

        planet_name = self.__planetNames[planet_index]
        if planet_name in self.__selectedPlanetNames:
            self.__highlight_connected_trade_routes(planet_index)

        for trade_route in self.__allTradeRoutes:
            if trade_route.start.name != planet_name and trade_route.end.name != planet_name:
                continue

            line = self.__plot_trade_route(
                trade_route,
                alpha=0.25,
                linewidth=1.0,
                linestyle="--",
                zorder=0,
            )
            self.__tradeRoutePreviewLines.append(line)

    def __plot_trade_route(self, trade_route, **style):
        return self.__axes.plot(
            [trade_route.start.x, trade_route.end.x],
            [trade_route.start.y, trade_route.end.y],
            color=self.__routeColor,
            **style,
        )[0]

    def __highlight_connected_trade_routes(self, planet_index: int) -> None:
        """Highlight routes connected to the hovered planet."""
        if planet_index < 0 or planet_index >= len(self.__planetNames):
            self.__reset_trade_route_highlight()
            return

        hovered_planet_name = self.__planetNames[planet_index]
        for line, (start_name, end_name) in zip(
            self.__tradeRouteLines, self.__tradeRouteConnections
        ):
            is_connected = hovered_planet_name == start_name or hovered_planet_name == end_name
            line.set_color("gold" if is_connected else self.__routeColor)
            line.set_alpha(0.9 if is_connected else 0.1)
            line.set_linewidth(2.0 if is_connected else 1.0)
            line.set_zorder(5 if is_connected else 1)

    def __update_annotation(self, ind) -> None:
        """Updates annotation parameters"""
        pos = self.__planetsScatter.get_offsets()[ind["ind"][0]]
        self.__annotate.xy = pos
        text = "\n".join(
            "Planet: {} \nFaction: {} \nStarbase: {} \nShipyard: {} \nGround Slots: {} \nIncome: {} \nSupports: {}".format(
                self.__planetNames[n],
                self.__planetOwners[n],
                self.__starbaseLevel[n],
                self.__shipyardLevel[n],
                self.__groundStructureSlots[n],
                self.__income[n],
                self.__SupportsStructure[n],
            )
            for n in ind["ind"]
        )
        self.__annotate.set_text(text)

    def TraceTradeRoute(self, ind) -> None:
        """Handler for tracing a traderoute between planets on plot"""
        """Trace movement is handled in __planetHover"""
        self.__tradeRouteTraceStart = ind
