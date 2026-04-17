import sys

from PyQt6.QtWidgets import QApplication

from commands.ShowTradeCreatorDialogCommand import ShowTradeRouteCreatorDialogCommand
from commands.ShowCampaignPropertiesDialogCommand import (
    ShowCampaignCreatorDialogCommand,
)
from commands.ShowAutoConnectionSettingsCommand import AutoConnectionSettingsCommand
from commands.ShowOptionsDialogCommand import ShowOptionsDialogCommand
from config import Config
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter
from ui.planetcontextmenu import PlanetContextMenu
from ui.qtmainwindow import QtMainWindow
from RepositoryCreator import RepositoryCreator


def main(argv=None, start_event_loop: bool = True) -> int:
    config: Config = Config()
    args = argv if argv is not None else sys.argv

    if len(args) > 1:
        dataFolders = [args[1]]
    else:
        dataFolders = config.dataFolders

    app = QApplication([])

    repositoryCreator: RepositoryCreator = RepositoryCreator()
    repository = repositoryCreator.constructRepository(
        dataFolders, config.startingForcesLibraryURL
    )

    dialogFactory = DialogFactory(repository)

    qtMainWindow: QtMainWindow = QtMainWindow()
    presenter: MainWindowPresenter = MainWindowPresenter(
        qtMainWindow, repository, config
    )
    presenter.newTradeRouteCommand = ShowTradeRouteCreatorDialogCommand(
        presenter, dialogFactory
    )
    presenter.campaignPropertiesCommand = ShowCampaignCreatorDialogCommand(
        presenter, dialogFactory
    )
    presenter.planetContextMenu = PlanetContextMenu(presenter)
    presenter.autoConnectionSettingsCommand = AutoConnectionSettingsCommand(
        presenter, dialogFactory
    )
    presenter.optionsDialogCommand = ShowOptionsDialogCommand(presenter, dialogFactory)

    qtMainWindow.setMainWindowPresenter(presenter)
    qtMainWindow.getWindow().show()

    if start_event_loop:
        return app.exec()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
