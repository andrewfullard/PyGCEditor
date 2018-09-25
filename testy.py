import random

from PyQt5.QtWidgets import QApplication

from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtmainwindow import QtMainWindow


repository: GameObjectRepository = GameObjectRepository()

a = Planet("A")
a.x = random.randint(-100, 100)
a.y = random.randint(-100, 100)
b = Planet("B")
b.x = random.randint(-100, 100)
b.y = random.randint(-100, 100)
c = Planet("C")
c.x = random.randint(-100, 100)
c.y = random.randint(-100, 100)
d = Planet("D")
d.x = random.randint(-100, 100)
d.y = random.randint(-100, 100)

repository.addPlanet(a)
repository.addPlanet(b)
repository.addPlanet(c)
repository.addPlanet(d)

app = QApplication([])

qtMainWindow: QtMainWindow = QtMainWindow()
presenter: MainWindowPresenter = MainWindowPresenter(qtMainWindow, repository)
qtMainWindow.setMainWindowPresenter(presenter)
qtMainWindow.getWindow().show()

app.exec_()
