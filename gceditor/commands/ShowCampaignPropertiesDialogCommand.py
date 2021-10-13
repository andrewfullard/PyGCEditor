from gceditor.commands.Command import Command
from gceditor.gameObjects.campaign import Campaign
from gceditor.ui.qtcampaignproperties import QtCampaignProperties
from gceditor.ui.dialogs import Dialog, DialogResult
from gceditor.ui.DialogFactory import DialogFactory
from gceditor.ui.mainwindow_presenter import MainWindowPresenter

class ShowCampaignCreatorDialogCommand(Command):
    '''Class to handle displaying the campaign creator dialog box'''
    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter

    def execute(self, name = -1) -> None:
        '''Runs the dialog and passes results to the presenter and repository'''
        dialog = self.__dialogFactory.makeCampaignPropertiesDialog()
        result: DialogResult = dialog.show(name)

        if result is DialogResult.Ok and name == -1:
            campaign: Campaign = dialog.getCampaignProperties()
            self.__presenter.onNewCampaign(campaign)