from commands.Command import Command
from ui.dialogs import DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter


class ShowOptionsDialogCommand(Command):
    """Class to handle displaying the options dialog box."""

    def __init__(
        self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory
    ):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter

    def execute(self) -> None:
        dialog = self.__dialogFactory.makeOptionsDialog()
        config = self.__presenter.config

        result: DialogResult = dialog.show(
            config.modPath,
            config.submods,
            config.autoPlanetConnectionDistance,
            config.startingForcesLibraryURL,
        )

        if result is DialogResult.Ok:
            self.__presenter.onConfigChanged(
                dialog.getModPath(),
                dialog.getSubmods(),
                dialog.getAutoConnectionDistance(),
                dialog.getStartingForcesLibraryURL(),
            )
