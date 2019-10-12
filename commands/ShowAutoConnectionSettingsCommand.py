from commands.Command import Command
from ui.dialogs import Dialog, DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter

class AutoConnectionSettingsCommand(Command):
    '''Class to handle displaying the trade route creator dialog box'''
    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter

    def execute(self) -> None:
        '''Runs the dialog and passes results to the presenter and repository'''
        dialog = self.__dialogFactory.makeAutoConnectionSettingsDialog()
        result: DialogResult = dialog.show(self.__presenter.config.autoPlanetConnectionDistance, self.__presenter.showAutoConnections)

        if result is DialogResult.Ok:
            autoConnectionDistance: int = dialog.getDistance()
            showAutoConnections: bool = dialog.getShowAutoConnections()
            self.__presenter.onAutoConnectionSettingChanged(autoConnectionDistance, showAutoConnections)