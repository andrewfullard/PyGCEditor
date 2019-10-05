from commands.Command import Command
from ui.dialogs import Dialog, DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter
from xmlUtil.xmlstructure import XMLStructure

class ShowPlanetFileHiderCommand(Command):
    '''Class to handle displaying the trade route creator dialog box'''
    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter

    def execute(self) -> None:
        '''Runs the dialog and passes results to the presenter and repository'''
        dialog = self.__dialogFactory.makePlanetFileHiderDialog()
        result: DialogResult = dialog.show(XMLStructure.planetFiles, self.__presenter.planetFileBlacklist)

        if result is DialogResult.Ok:
            hiddenFileList: int = dialog.getHiddenFiles()
            self.__presenter.onPlanetFileBlacklistUpdated(hiddenFileList)