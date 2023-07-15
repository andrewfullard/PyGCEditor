from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal
from matplotlib.backends.backend_qtagg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Axes, Figure


class QtGalacticPlot(QWidget):
    '''Class for plotting the galaxy'''
    #signal to send to main window presenter when a planet is selected in the plot
    planetSelectedSignal = pyqtSignal(int)
    planetShiftSelectedSignal = pyqtSignal(int)

    def __init__(self, parent: QWidget = None):
        super(QtGalacticPlot, self).__init__()
        self.__galacticPlotWidget: QWidget = QWidget(parent)
        self.__galacticPlotWidget.setLayout(QVBoxLayout())
        self.__is_first_run = True

        self.__galacticPlotCanvas: FigureCanvas = FigureCanvas(Figure())

        self.__galacticPlotCanvas.mpl_connect('pick_event', self.__planetSelect)
        self.__galacticPlotCanvas.mpl_connect('motion_notify_event', self.__planetHover)

        self.__galacticPlotNavBar: NavigationToolbar = NavigationToolbar(self.__galacticPlotCanvas, self.__galacticPlotWidget)
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotNavBar)
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotCanvas)
        self.__axes: Axes = self.__galacticPlotCanvas.figure.add_subplot(111, aspect = "equal")

        self.__annotate = self.__axes.annotate("", xy = (0,0), xytext = (10, 10), textcoords = "offset points", bbox = dict(boxstyle="round", fc="w"), arrowprops = dict(arrowstyle="->"), zorder = 9)
        self.__annotate.set_visible(False)
        self.__planetNames = []
        self.__planetOwners = []
        self.__planetsScatter = None

    def plotGalaxy(self, planets, tradeRoutes, allPlanets, planetOwners = [], autoPlanetConnectionDistance: int = 0) -> None:
        '''Plots all planets as alpha = 0.1, then overlays all selected planets and trade routes'''
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

        #Has to be set again here for the planet hover labels to work
        self.__annotate = self.__axes.annotate("", xy = (0,0), xytext = (10, 10), textcoords = "offset points", bbox = dict(boxstyle="round", fc="w"), arrowprops = dict(arrowstyle="->"), zorder = 9)
        self.__annotate.set_visible(False)

        self.__planetNames = []
        self.__planetOwners = []

        x = []
        y = []

        for ap in allPlanets:
            found_pa = False
            for pa, po in zip(planets, planetOwners):
                if ap.name == pa.name:
                    self.__planetOwners.append(po.name)
                    found_pa = True
            if found_pa == False:
                self.__planetOwners.append("")

        for p in allPlanets:
            x.append(p.x)
            y.append(p.y)
            self.__planetNames.append(p.name)

        self.__planetsScatter = self.__axes.scatter(x, y, c = 'grey', alpha = 0.1, picker = 5, zorder=2)

        x1 = 0        
        y1 = 0
        x2 = 0
        y2 = 0

        # loop through routes
        for t in tradeRoutes:
            x1 = t.start.x
            y1 = t.start.y
            x2 = t.end.x
            y2 = t.end.y
            # plot each route (start, end)            
            self.__axes.plot([x1, x2], [y1, y2], 'k-', alpha=0.4, zorder=1)
        
        #Create automatic connections between planets
        if autoPlanetConnectionDistance > 0:
            for p1 in planets:
                for p2 in planets:
                    if p1 == p2:
                        break
                    dist: float = p1.distanceTo(p2)
                    if dist < autoPlanetConnectionDistance:
                        self.__axes.plot([p1.x, p2.x], [p1.y, p2.y], 'k-', alpha=0.1, zorder=1)

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

            self.__axes.scatter(x, y, c = color, edgecolors = 'black', zorder=4)
        else:
            for p in planets:
                x.append(p.x)
                y.append(p.y)

            self.__axes.scatter(x, y, c = 'grey', zorder=3)

        self.__galacticPlotCanvas.draw_idle()


    def getWidget(self) -> QWidget:
        '''Returns the plot widget'''
        return self.__galacticPlotWidget

    def __planetSelect(self, event) -> None:
        '''Event handler for selecting a planet on the map'''
        planet_index = event.ind[0]
        if event.mouseevent.button == 3:
            self.planetShiftSelectedSignal.emit(planet_index)
        else:
            self.planetSelectedSignal.emit(planet_index)

    def __planetHover(self, event) -> None:
        '''Handler for hovering on a planet in the plot'''
        visible = self.__annotate.get_visible()

        if event.inaxes == self.__axes:
            if self.__planetsScatter:
                contains, ind = self.__planetsScatter.contains(event)
            else:
                contains = False

            if contains:
                self.__update_annotation(ind)
                self.__annotate.set_visible(True)
                self.__galacticPlotCanvas.draw_idle()
            else:
                if visible:
                    self.__annotate.set_visible(False)
                    self.__galacticPlotCanvas.draw_idle()

    def __update_annotation(self, ind) -> None:
        '''Updates annotation parameters'''
        pos = self.__planetsScatter.get_offsets()[ind["ind"][0]]
        self.__annotate.xy = pos
        text = "\n".join("{} [{}]".format(self.__planetNames[n], self.__planetOwners[n]) for n in ind["ind"])
        self.__annotate.set_text(text)