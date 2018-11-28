from commands.Command import Command
from gameObjects.campaign import Campaign
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.qtcampaignproperties import QtCampaignProperties
from ui.dialogs import Dialog, DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter

class ShowCampaignCreatorDialogCommand(Command):
    '''Class to handle displaying the campaign creator dialog box'''

    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory, repository: GameObjectRepository):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter
        self.__repository = repository

    def execute(self) -> None:
        '''Runs the dialog and passes results to the presenter and repository'''
        currentCampaign = self.__presenter.getSelectedCampaign()    
        dialog = self.__dialogFactory.makeCampaignPropertiesDialog(currentCampaign)
        result: DialogResult = dialog.show()

        if result is DialogResult.Ok:
            campaign: Campaign = dialog.getCampaignProperties()
            if currentCampaign is None or campaign.name != currentCampaign.name:
                self.__repository.addCampaign(campaign)
                self.__presenter.onNewCampaign(campaign)
            else:
                self.__presenter.onCampaignUpdate(campaign)