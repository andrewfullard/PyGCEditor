from commands.Command import Command
from gameObjects.campaign import Campaign
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.qtcampaignproperties import QtCampaignProperties
from ui.dialogs import Dialog, DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter

class ShowCampaignCreatorDialogCommand(Command):

    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory, repository: GameObjectRepository):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter
        self.__repository = repository

    def execute(self, name = -1) -> None:
        dialog = self.__dialogFactory.makeCampaignPropertiesDialog()
        result: DialogResult = dialog.show(name)

        if result is DialogResult.Ok:
            campaign: Campaign = dialog.getCampaignProperties()
            if not campaign in self.__repository.campaigns:
                self.__repository.addCampaign(campaign)
                self.__presenter.onNewCampaign(campaign)