from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit

from gameObjects.campaign import Campaign
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.dialogs import Dialog, DialogResult

class QtCampaignProperties:
    '''Class for a "campaign properties" dialog box'''
    def __init__(self, repository: GameObjectRepository):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__inputName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputSetName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputSortOrder: QLineEdit = QLineEdit(self.__dialog)
        self.__inputTextID: QLineEdit = QLineEdit(self.__dialog)
        self.__inputDescriptionText: QLineEdit = QLineEdit(self.__dialog)
        self.__startingActivePlayer: QLineEdit = QLineEdit(self.__dialog)
        self.__rebelStoryName: QLineEdit = QLineEdit(self.__dialog)
        self.__empireStoryName: QLineEdit = QLineEdit(self.__dialog)
        self.__underworldStoryName: QLineEdit = QLineEdit(self.__dialog)
      
        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)
        
        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("Campaign Name", self.__inputName)
        self.__formLayout.addRow("Campaign Set Name", self.__inputSetName)
        self.__formLayout.addRow("Text ID", self.__inputTextID)
        self.__formLayout.addRow("Sort Order", self.__inputSortOrder)
        self.__formLayout.addRow("Description Text", self.__inputDescriptionText)
        self.__formLayout.addRow("Starting Active Player", self.__startingActivePlayer)
        self.__formLayout.addRow("Rebel Story Name", self.__rebelStoryName)
        self.__formLayout.addRow("Empire Story Name", self.__empireStoryName)
        self.__formLayout.addRow("Underworld Story Name", self.__underworldStoryName)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)
        
        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("Campaign Properties")      
        self.__dialog.setLayout(self.__layout)
        self.__dialog.resize(500, 300)

        self.__result = DialogResult.Cancel

        self.__repository = repository

        self.__name = ""
        self.__setName = ""
       
    def show(self, name = -1) -> DialogResult:
        '''Display dialog modally'''
        if name is not -1:
            campaignList = list(self.__repository.campaigns)
            campaign = next((x for x in campaignList if x.name == name), None)
            if campaign is not None:
                self.__inputName.setText(campaign.name)
                self.__inputSetName.setText(campaign.setName)
                self.__inputSortOrder.setText(campaign.sortOrder)
                self.__inputTextID.setText(campaign.textID)
                self.__inputDescriptionText.setText(campaign.descriptionText)
                self.__startingActivePlayer.setText(campaign.startingActivePlayer)
                self.__rebelStoryName.setText(campaign.rebelStoryName)
                self.__empireStoryName.setText(campaign.empireStoryName)
                self.__underworldStoryName.setText(campaign.underworldStoryName)
            else:
                print("Campaign " + campaign + " missing from repository")

        self.__dialog.exec()
        return self.__result

    def getCampaignProperties(self) -> Campaign:
        '''Returns the Campaign properties'''
        campaign: Campaign = Campaign(self.__name)
        campaign.setName = self.__inputSetName.text()
        campaign.sortOrder = self.__inputSortOrder.text()
        campaign.textID = self.__inputTextID.text()
        campaign.descriptionText = self.__inputDescriptionText.text()
        campaign.startingActivePlayer = self.__startingActivePlayer.text()
        campaign.rebelStoryName = self.__rebelStoryName.text()
        campaign.empireStoryName = self.__empireStoryName.text()
        campaign.underworldStoryName = self.__underworldStoryName.text()

        return campaign 

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking'''
        self.__name = self.__inputName.text()

        if len(self.__name) == 0:
            print("Error! No campaign name set!")

        self.__result = DialogResult.Ok
        self.__dialog.close()

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()