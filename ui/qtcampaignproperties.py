from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit, QCheckBox

from gameObjects.campaign import Campaign
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.dialogs import Dialog, DialogResult

class QtCampaignProperties:
    '''Class for a "campaign properties" dialog box'''
    def __init__(self, campaign = Campaign()):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__inputName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputSetName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputSortOrder: QLineEdit = QLineEdit(self.__dialog)
        self.__inputTextID: QLineEdit = QLineEdit(self.__dialog)
        self.__inputDescriptionText: QLineEdit = QLineEdit(self.__dialog)
        self.__eraStart: QLineEdit = QLineEdit(self.__dialog)
        self.__rebelStoryName: QLineEdit = QLineEdit(self.__dialog)
        self.__empireStoryName: QLineEdit = QLineEdit(self.__dialog)
        self.__underworldStoryName: QLineEdit = QLineEdit(self.__dialog)
        self.__storyName: QLineEdit = QLineEdit(self.__dialog)
        self.__isListed: QLineEdit = QLineEdit(self.__dialog)
        self.__useDefaultForces: QCheckBox = QCheckBox(self.__dialog)
     
        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)
        
        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("Campaign Name", self.__inputName)
        self.__formLayout.addRow("Campaign Set Name", self.__inputSetName)
        self.__formLayout.addRow("Text ID", self.__inputTextID)
        self.__formLayout.addRow("Sort Order", self.__inputSortOrder)
        self.__formLayout.addRow("Description Text", self.__inputDescriptionText)
        self.__formLayout.addRow("Starting Era", self.__eraStart)
        self.__formLayout.addRow("Rebel Story Name", self.__rebelStoryName)
        self.__formLayout.addRow("Empire Story Name", self.__empireStoryName)
        self.__formLayout.addRow("Underworld Story Name", self.__underworldStoryName)
        self.__formLayout.addRow("Story Name", self.__storyName)
        self.__formLayout.addRow("Show Campaign", self.__isListed)
        self.__formLayout.addRow("Use default starting forces?", self.__useDefaultForces)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)
        
        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("Campaign Properties")      
        self.__dialog.setLayout(self.__layout)
        self.__dialog.resize(500, 300)

        self.__result = DialogResult.Cancel

        

        # self.__repository = repository

        self.__name = ""
        self.__setName = ""

        self.__campaign = campaign or Campaign()
       
    def show(self) -> DialogResult:
        '''Display dialog modally'''

        self.__inputName.setText(self.__campaign.name)
        self.__inputSetName.setText(self.__campaign.setName)
        self.__inputSortOrder.setText(self.__campaign.sortOrder)
        self.__inputTextID.setText(self.__campaign.textID)
        self.__inputDescriptionText.setText(self.__campaign.descriptionText)
        self.__eraStart.setText(self.__campaign.eraStart)
        self.__rebelStoryName.setText(self.__campaign.rebelStoryName)
        self.__empireStoryName.setText(self.__campaign.empireStoryName)
        self.__underworldStoryName.setText(self.__campaign.underworldStoryName)
        self.__storyName.setText(self.__campaign.storyName)
        self.__isListed.setText(self.__campaign.isListed)
        self.__useDefaultForces.setChecked(self.__campaign.useDefaultForces)

        self.__dialog.exec()
        return self.__result

    def getCampaignProperties(self) -> Campaign:
        '''Returns the Campaign properties'''

        self.__campaign.name = self.__inputName.text()
        self.__campaign.setName = self.__inputSetName.text()
        self.__campaign.sortOrder = self.__inputSortOrder.text()
        self.__campaign.textID = self.__inputTextID.text()
        self.__campaign.descriptionText = self.__inputDescriptionText.text()
        self.__campaign.eraStart = self.__eraStart.text()
        self.__campaign.rebelStoryName = self.__rebelStoryName.text()
        self.__campaign.empireStoryName = self.__empireStoryName.text()
        self.__campaign.underworldStoryName = self.__underworldStoryName.text()
        self.__campaign.storyName = self.__storyName.text()
        self.__campaign.isListed = self.__isListed.text()
        self.__campaign.useDefaultForces = self.__useDefaultForces.isChecked()

        return self.__campaign 

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