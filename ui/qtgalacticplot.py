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
        self.__axes: Axes = self.__galacticPlotCanvas.figure.add_subplot(111, aspect = "equal")

    #plots galaxy
    def plotGalaxy(self, planets, tradeRoutes, allPlanets):
        self.__axes.clear()

        x = []
        y = []

        for p in allPlanets:
            x.append(p.x)
            y.append(p.y)

        self.__axes.scatter(x, y, c = 'b', alpha = 0.1)

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

        for p in planets:
            x.append(p.x)
            y.append(p.y)
            self.__axes.text(p.x+1, p.y+1, p.name, fontsize=10)

        self.__axes.scatter(x, y, c = 'b')

        self.__galacticPlotCanvas.draw_idle()


    def getWidget(self) -> QWidget:
        return self.__galacticPlotWidget
