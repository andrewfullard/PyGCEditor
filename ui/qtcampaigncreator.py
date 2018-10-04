from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit

from gameObjects.campaign import Campaign

class QtCampaignCreator:
    '''Class for a "new campaign" dialog box'''
    def __init__(self):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__inputName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputSetName: QLineEdit = QLineEdit(self.__dialog)
      
        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)
        
        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("Campaign Name", self.__inputName)
        self.__formLayout.addRow("Campaign Set Name", self.__inputSetName)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)
        
        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("New Campaign")      
        self.__dialog.setLayout(self.__layout)
       
    def showDialog(self) -> None:
        '''Display dialog modally'''
        self.__dialog.exec_()

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking and adds campaign to repository'''
        name = self.__inputName.text()
        setName = self.__inputSetName.text()

        if len(name) > 0:
            newcampaign = Campaign(name)
        else:
            print("Error! No campaign name set!")
        
        if len(setName) > 0:
            newcampaign.setName = setName
        
        #Add campaign to repository here
        self.__dialog.close()

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()