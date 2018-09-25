from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Axes, Figure


class QtGalacticPlot:

    def __init__(self, parent: QWidget = None):
        self.__galacticPlotWidget: QWidget = QWidget(parent)
        self.__galacticPlotWidget.setLayout(QVBoxLayout())

        self.__galacticPlotCanvas: FigureCanvas = FigureCanvas(Figure())
        self.__galacticPlotNavBar: NavigationToolbar = NavigationToolbar(self.__galacticPlotCanvas, self.__galacticPlotWidget)
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotNavBar)
        self.__galacticPlotWidget.layout().addWidget(self.__galacticPlotCanvas)
        self.__axes: Axes = self.__galacticPlotCanvas.figure.add_subplot(111)

    # plots planets as standard blue circles
    def plotPlanets(self, planets):
        self.__axes.clear()
        x = []
        y = []

        for p in planets:
            x.append(p.x)
            y.append(p.y)

        self.__axes.scatter(x, y)
        self.__galacticPlotCanvas.draw_idle()
    
    # plots traderoutes as rainbow fluorescent lines
    def plotTradeRoutes(self, tradeRoutes):
        # initialize traderoute start/end x,y positions
        self.__axes.clear()
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
            self.__axes.plot([x1, x2], [y1, y2], 'k-')

        self.__galacticPlotCanvas.draw_idle()

    def getWidget(self) -> QWidget:
        return self.__galacticPlotWidget
