import logging
import sys
from threading import Event
from typing import cast

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEventLoop, QThread

from commands.ShowTradeCreatorDialogCommand import ShowTradeRouteCreatorDialogCommand
from commands.ShowCampaignPropertiesDialogCommand import (
    ShowCampaignCreatorDialogCommand,
)
from commands.ShowAutoConnectionSettingsCommand import AutoConnectionSettingsCommand
from commands.ShowOptionsDialogCommand import ShowOptionsDialogCommand
from config import Config
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.DialogFactory import DialogFactory
from ui.qtloadinglogdialog import QtLoadingLogDialog, QtLogHandler
from ui.repositoryloader import RepositoryLoader, RepositoryLoadResult
from ui.mainwindow_presenter import MainWindowPresenter
from ui.planetcontextmenu import PlanetContextMenu
from ui.qtmainwindow import QtMainWindow
from RepositoryCreator import RepositoryCreator


def main(argv=None, start_event_loop: bool = True) -> int:
    logging.basicConfig(level=logging.INFO)
    app = QApplication([])
    loadingDialog = QtLoadingLogDialog()
    loadingDialog.beginLoading()
    logging.getLogger().addHandler(QtLogHandler(loadingDialog))

    config: Config = Config()
    loadingDialog.setLoadingPaths(config.modPath, config.submods, config.startingForcesLibraryURL)
    args = argv if argv is not None else sys.argv

    if len(args) > 1:
        dataFolders = [args[1]]
    else:
        dataFolders = config.dataFolders

    loadingLoop = QEventLoop()
    loadingThread = QThread()
    cancellationEvent = Event()
    loader = RepositoryLoader(
        dataFolders,
        config.startingForcesLibraryURL,
        repositoryCreatorFactory=RepositoryCreator,
        cancellationEvent=cancellationEvent,
    )
    repositoryResult = RepositoryLoadResult(loadingLoop, loadingThread)
    loader.moveToThread(loadingThread)
    loadingThread.started.connect(loader.load)
    loader.progress.connect(loadingDialog.updateProgress)
    loader.loaded.connect(repositoryResult.setRepository)
    loader.failed.connect(repositoryResult.setError)
    loadingCancelledState = [False]
    loadingCancelled = getattr(loadingDialog, "loadingCancelled", None)
    if loadingCancelled is not None:
        loadingCancelled.connect(
            lambda: (loadingCancelledState.__setitem__(0, True), cancellationEvent.set())
        )
        loadingCancelled.connect(loadingLoop.quit)
        loadingCancelled.connect(app.quit)

    loadingThread.start()
    loadingLoop.exec()
    if loadingCancelledState[0]:
        loadingThread.terminate()
        loadingThread.wait()
        return 0
    loadingThread.wait()

    if repositoryResult.error is not None:
        raise repositoryResult.error

    if repositoryResult.repository is None:
        raise RuntimeError("Repository loading completed without a repository")

    repository = cast(GameObjectRepository, repositoryResult.repository)

    dialogFactory = DialogFactory(repository)

    qtMainWindow: QtMainWindow = QtMainWindow()
    qtMainWindow.setLoadingLogDialog(loadingDialog)
    presenter: MainWindowPresenter = MainWindowPresenter(
        qtMainWindow, repository, config, dialogFactory
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
    loadingDialog.completeLoading()
    qtMainWindow.getWindow().show()

    if start_event_loop:
        return app.exec()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
