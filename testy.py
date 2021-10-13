import sys

from PyQt5.QtWidgets import QApplication

from gceditor.commands.ShowTradeCreatorDialogCommand import ShowTradeRouteCreatorDialogCommand
from gceditor.commands.ShowCampaignPropertiesDialogCommand import ShowCampaignCreatorDialogCommand
from gceditor.commands.ShowAutoConnectionSettingsCommand import AutoConnectionSettingsCommand
from config import Config
from gceditor.ui.DialogFactory import DialogFactory
from gceditor.ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from gceditor.ui.planetcontextmenu import PlanetContextMenu
from gceditor.ui.qtmainwindow import QtMainWindow
from gceditor.RepositoryCreator import RepositoryCreator

config: Config = Config()

numArgs = len(sys.argv)

if numArgs > 1:
    path = sys.argv[1]
else:
    path = config.dataPath

app = QApplication([])

repositoryCreator: RepositoryCreator = RepositoryCreator()
repository = repositoryCreator.constructRepository(path)

dialogFactory = DialogFactory(repository)

qtMainWindow: QtMainWindow = QtMainWindow()
presenter: MainWindowPresenter = MainWindowPresenter(qtMainWindow, repository, config)
presenter.newTradeRouteCommand = ShowTradeRouteCreatorDialogCommand(presenter, dialogFactory)
presenter.campaignPropertiesCommand = ShowCampaignCreatorDialogCommand(presenter, dialogFactory)
presenter.planetContextMenu = PlanetContextMenu(presenter)
presenter.autoConnectionSettingsCommand = AutoConnectionSettingsCommand(presenter, dialogFactory)

qtMainWindow.setMainWindowPresenter(presenter)
qtMainWindow.getWindow().show()

app.exec_()
