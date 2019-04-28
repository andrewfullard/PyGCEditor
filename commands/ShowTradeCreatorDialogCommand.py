from commands.Command import Command
from gameObjects.traderoute import TradeRoute
from ui.qttraderoutecreator import QtTradeRouteCreator
from ui.dialogs import Dialog, DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter

class ShowTradeRouteCreatorDialogCommand(Command):
    '''Class to handle displaying the trade route creator dialog box'''
    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter

    def execute(self) -> None:
        '''Runs the dialog and passes results to the presenter and repository'''
        dialog = self.__dialogFactory.makeTradeRouteCreationDialog()
        result: DialogResult = dialog.show()

        if result is DialogResult.Ok:
            tradeRoute: TradeRoute = dialog.getCreatedTradeRoute()
            self.__presenter.onNewTradeRoute(tradeRoute)