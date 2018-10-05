import random
import sys

from PyQt5.QtWidgets import QApplication

from RepositoryCreator import RepositoryCreator
from config import Config
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtmainwindow import QtMainWindow

repositoryCreator: repositoryCreator = RepositoryCreator()
config: config = Config()

numArgs = len(sys.argv)

if numArgs > 1:
    repository = repositoryCreator.constructRepository(sys.argv[1])
else:
    repository = repositoryCreator.constructRepository(config.dataPath)


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
