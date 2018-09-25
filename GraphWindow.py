import random

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MainWindow:

    def __init__(self):
        self.__window: QMainWindow = QMainWindow()
        self.__widget: QWidget = QWidget(self.__window)
        self.__widget.setLayout(QVBoxLayout())

        self.__canvas: FigureCanvas = FigureCanvas(Figure())
        self.__navBar: NavigationToolbar = NavigationToolbar(self.__canvas, self.__window)
        self.__widget.layout().addWidget(self.__navBar)
        self.__widget.layout().addWidget(self.__canvas)

        self.__window.setCentralWidget(self.__widget)

        x = []
        y = []
        numPoints = random.randint(10, 100)

        for i in range(0, numPoints):
            x.append(random.randint(0, 50))
            y.append(random.randint(0, 50))

        self.__canvas.figure.add_subplot(111).scatter(x, y)

    def getWindow(self) -> QMainWindow:
        return self.__window




app: QApplication = QApplication([])

window: MainWindow = MainWindow()
window.getWindow().show()

app.exec_()
