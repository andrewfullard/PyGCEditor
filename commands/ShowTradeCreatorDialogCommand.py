from commands.Command import Command
from gameObjects.traderoute import TradeRoute
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.qttraderoutecreator import QtTradeRouteCreator
from ui.dialogs import Dialog, DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter

class ShowTradeRouteCreatorDialogCommand(Command):
    '''Class to handle displaying the trade route creator dialog box'''
    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory, repository: GameObjectRepository):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter
        self.__repository = repository

    def execute(self) -> None:
        '''Runs the dialog and passes results to the presenter and repository'''
        dialog = self.__dialogFactory.makeTradeRouteCreationDialog()
        result: DialogResult = dialog.show()

        if result is DialogResult.Ok:
            tradeRoute: TradeRoute = dialog.getCreatedTradeRoute()
            self.__repository.addTradeRoute(tradeRoute)
            self.__presenter.onNewTradeRoute(tradeRoute)