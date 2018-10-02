import random
import sys

from PyQt5.QtWidgets import QApplication

from gameObjects.gameObjectRepository import GameObjectRepository
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from gameObjects.campaign import Campaign
from xml.xmlreader import XMLReader
from xml.xmlstructure import XMLStructure
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtmainwindow import QtMainWindow


numArgs = len(sys.argv)

if numArgs > 1:
    XMLStructure.dataFolder = sys.argv[1]
else:
    XMLStructure.dataFolder = "C:/Program Files (x86)/Steam/SteamApps/common/Star Wars Empire at War/corruption/Mods/Source/Data"

repository: GameObjectRepository = GameObjectRepository()

campaignfile = XMLStructure.dataFolder + "/XML/CampaignFiles.XML"
planetfile = XMLStructure.dataFolder + "/XML/Planets.XML"
traderoutefile = XMLStructure.dataFolder + "/XML/TradeRoutes.XML"

xml: XMLReader = XMLReader()

xmlfilelist = [planetfile, traderoutefile]

rootlist = xml.parseXMLFileList(xmlfilelist)

planetsfromxml = xml.getNamesFromXML(rootlist[0])
traderoutesfromxml = xml.getNamesFromXML(rootlist[1])

campaignrootlist = xml.findMetaFileRefs(campaignfile)

campaignNames = []
allCampaignRoots = []

# All this needs to be in classes I expect

for campaignroot in campaignrootlist:
    campaignNames.extend(xml.getNamesFromXML(campaignroot))
    allCampaignRoots.extend(campaignroot.iter("Campaign"))

for planet in planetsfromxml:
    newplanet = Planet(planet)
    newplanet.x, newplanet.y = xml.getLocation(planet, rootlist[0])
    repository.addPlanet(newplanet)

for route in traderoutesfromxml:
    newroute = TradeRoute(route)
    newroute.start, newroute.end = xml.getStartEnd(route, repository.planets, rootlist[1])
    repository.addTradeRoute(newroute)

for (campaign, campaignroot) in zip(campaignNames, allCampaignRoots):
    newCampaignPlanets = set()
    newCampaignTradeRoutes = set()

    newcampaign = Campaign(campaign)
    campaignPlanetNames = xml.getListFromXMLRoot(campaignroot, ".//Locations")
    campaignTradeRouteNames = xml.getListFromXMLRoot(campaignroot, ".//Trade_Routes")

    for p in campaignPlanetNames:
        newplanet = xml.getPlanet(p, repository.planets)
        newCampaignPlanets.add(newplanet)

    for t in campaignTradeRouteNames:
        newroute = xml.getPlanet(t, repository.tradeRoutes)
        newCampaignTradeRoutes.add(newroute)

    newcampaign.planets = newCampaignPlanets
    newcampaign.tradeRoutes = newCampaignTradeRoutes

    repository.addCampaign(newcampaign)


# a = Planet("A")
# a.x = random.randint(-100, 100)
# a.y = random.randint(-100, 100)
# b = Planet("B")
# b.x = random.randint(-100, 100)
# b.y = random.randint(-100, 100)
# c = Planet("C")
# c.x = random.randint(-100, 100)
# c.y = random.randint(-100, 100)
# d = Planet("D")
# d.x = random.randint(-100, 100)
# d.y = random.randint(-100, 100)

# repository.addPlanet(a)
# repository.addPlanet(b)
# repository.addPlanet(c)
# repository.addPlanet(d)

# ab_trade = TradeRoute("1 to 2")
# ab_trade.start = list(repository.planets)[0]
# ab_trade.end = list(repository.planets)[1]
# print(ab_trade.name)
# repository.addTradeRoute(ab_trade)

app = QApplication([])

qtMainWindow: QtMainWindow = QtMainWindow()
presenter: MainWindowPresenter = MainWindowPresenter(qtMainWindow, repository)
qtMainWindow.setMainWindowPresenter(presenter)
qtMainWindow.getWindow().show()

app.exec_()
