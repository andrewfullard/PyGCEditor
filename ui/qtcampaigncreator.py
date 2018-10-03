from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit

class QtCampaignCreator:
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
        self.__dialog.exec_()

    def __okayClicked(self) -> None:
        self.__dialog.close()

    def __cancelClicked(self) -> None:
        self.__dialog.close()