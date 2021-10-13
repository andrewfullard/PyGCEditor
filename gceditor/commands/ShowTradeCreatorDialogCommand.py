from gceditor.commands.Command import Command
from gceditor.gameObjects.traderoute import TradeRoute
from gceditor.ui.qttraderoutecreator import QtTradeRouteCreator
from gceditor.ui.dialogs import Dialog, DialogResult
from gceditor.ui.DialogFactory import DialogFactory
from gceditor.ui.mainwindow_presenter import MainWindowPresenter

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