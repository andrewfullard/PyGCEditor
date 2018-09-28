import random

from PyQt5.QtWidgets import QApplication

from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from xml.xmlreader import XMLReader
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtmainwindow import QtMainWindow


repository: GameObjectRepository = GameObjectRepository()

""" planetfile = "C:/Program Files (x86)/Steam/SteamApps/common/Star Wars Empire at War/corruption/Mods/Source/Data/XML/Planets.XML"
traderoutefile = "C:/Program Files (x86)/Steam/SteamApps/common/Star Wars Empire at War/corruption/Mods/Source/Data/XML/TradeRoutes.XML"

xml: XMLReader = XMLReader()

xmlfilelist = [planetfile, traderoutefile]

rootlist = xml.parseXMLFileList(xmlfilelist)

planets = xml.getName(rootlist[0])

for planet in set(planets):
    newplanet = Planet(planet)
    newplanet.x, newplanet.y = xml.getLocation(planet, rootlist[0])
    repository.addPlanet(newplanet) """

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

ab_trade = TradeRoute("A to B")
ab_trade.start = list(repository.planets)[0]
ab_trade.end = list(repository.planets)[1]
print(ab_trade.name)
repository.addTradeRoute(ab_trade)

app = QApplication([])

qtMainWindow: QtMainWindow = QtMainWindow()
presenter: MainWindowPresenter = MainWindowPresenter(qtMainWindow, repository)
qtMainWindow.setMainWindowPresenter(presenter)
qtMainWindow.getWindow().show()

app.exec_()
