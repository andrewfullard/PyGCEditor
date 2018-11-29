from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Axes, Figure


class QtGalacticPlot(QWidget):
    '''Class for plotting the galaxy'''
    #signal to send to main window presenter when a planet is selected in the plot
    planetSelectedSignal = pyqtSignal(list)

    def __init__(self, parent: QWidget = None):
        super(QtGalacticPlot, self).__init__()
        self.__galacticPlotWidget: QWidget = QWidget(parent)
        self.__galacticPlotWidget.setLayout(QVBoxLayout())

        self.__galacticPlotCanvas: FigureCanvas = FigureCanvas(Figure())

        self.__galacticPlotCanvas.mpl_connect('pick_event', self.__planetSelect)
        self.__galacticPlotCanvas.mpl_connect('motion_notify_event', self.__planetHover)

        self.__galacticPlotNavBar: NavigationToolbar = NavigationToolbar(self.__galacticPlotCanvas, self.__galacticPlotWidget)
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotNavBar)
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotCanvas)
        self.__axes: Axes = self.__galacticPlotCanvas.figure.add_subplot(111, aspect = "equal")

        self.__annotate = self.__axes.annotate("", xy = (0,0), xytext = (10, 10), textcoords = "offset points", bbox = dict(boxstyle="round", fc="w"), arrowprops = dict(arrowstyle="->"))
        self.__annotate.set_visible(False)
        self.__planetNames = []
        self.__planetsScatter = None

    def plotGalaxy(self, planets, tradeRoutes, allPlanets, planetOwners = []) -> None:
        '''Plots all planets as alpha = 0.1, then overlays all selected planets and trade routes'''
        self.__axes.clear()

        #Has to be set again here for the planet hover labels to work
        self.__annotate = self.__axes.annotate("", xy = (0,0), xytext = (10, 10), textcoords = "offset points", bbox = dict(boxstyle="round", fc="w"), arrowprops = dict(arrowstyle="->"))
        self.__annotate.set_visible(False)

        self.__planetNames = []

        x = []
        y = []

        for p in allPlanets:
            x.append(p.x)
            y.append(p.y)
            self.__planetNames.append(p.name)

        self.__planetsScatter = self.__axes.scatter(x, y, c = 'grey', alpha = 0.1, picker = 5)

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
            self.__axes.plot([x1, x2], [y1, y2], 'k-', alpha=0.3)

        x = []
        y = []

        if planetOwners:        
            color = []
            for p, f in zip(planets, planetOwners):
                x.append(p.x)
                y.append(p.y)
                color.append(tuple(f.color))

            self.__axes.scatter(x, y, c = color, edgecolors = 'black')
        else:
            for p in planets:
                x.append(p.x)
                y.append(p.y)

            self.__axes.scatter(x, y, c = 'grey')

        self.__galacticPlotCanvas.draw_idle()


    def getWidget(self) -> QWidget:
        '''Returns the plot widget'''
        return self.__galacticPlotWidget

    def __planetSelect(self, event) -> None:
        '''Event handler for selecting a planet on the map'''
        planet_index = event.ind
        self.planetSelectedSignal.emit(list(planet_index))

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
        text = "{}".format(" ".join([self.__planetNames[n] for n in ind["ind"]]))
        self.__annotate.set_text(text)