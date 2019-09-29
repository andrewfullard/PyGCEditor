from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit, QCheckBox

from gameObjects.campaign import Campaign
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.dialogs import Dialog, DialogResult

class QtAutoConnectionSettings(Dialog):
    '''Class for a "Auto connections settings" dialog box'''
    def __init__(self, repository: GameObjectRepository):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__inputAutoConnectionDistance: QLineEdit = QLineEdit(self.__dialog)
        self.__toggleAutoConnectionVisibility: QCheckBox = QCheckBox("Hide auto planet connections", self.__dialog)

        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)

        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("Max distance for planets to auto-connect:", self.__inputAutoConnectionDistance)
        self.__formLayout.addRow("", self.__toggleAutoConnectionVisibility)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)

        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("Campaign Properties")
        self.__dialog.setLayout(self.__layout)

        self.__result = DialogResult.Cancel

        self.__repository = repository

        self.__distance: int = 0  #should be config value
        self.__connectionsVisible = True

    def show(self, currentDistance: int = 0, currentlyVisible: bool = True) -> DialogResult:
        '''Display dialog modally'''
        self.__distance = currentDistance
        self.__inputAutoConnectionDistance.setText(str(self.__distance))
        self.__toggleAutoConnectionVisibility.setChecked(not currentlyVisible)

        self.__dialog.exec()
        return self.__result

    def getDistance(self) -> int:
        '''Returns the required distance for auto connections'''
        return self.__distance

    def getShowAutoConnections(self) -> bool:
        '''Returns whether auto connections should be shown'''
        return self.__connectionsVisible

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking'''
        self.__distance = int(self.__inputAutoConnectionDistance.text())
        self.__connectionsVisible = not self.__toggleAutoConnectionVisibility.isChecked()

        self.__result = DialogResult.Ok
        self.__dialog.close()

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()