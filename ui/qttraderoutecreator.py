from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit

from gameObjects.traderoute import TradeRoute

class QtTradeRouteCreator:
    '''Class for a "new trade route" dialog box'''
    def __init__(self):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__inputName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputStart: QLineEdit = QLineEdit(self.__dialog)
        self.__inputEnd: QLineEdit = QLineEdit(self.__dialog)
      
        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)
        
        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("Trade Route Name", self.__inputName)
        self.__formLayout.addRow("Start Planet", self.__inputStart)
        self.__formLayout.addRow("End Planet", self.__inputEnd)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)
        
        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("New Trade Route")      
        self.__dialog.setLayout(self.__layout)

        self.__presenter = None
       
    def showDialog(self, presenter) -> None:
        '''Display dialog non-modally'''
        self.__presenter = presenter
        self.__dialog.show()

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking and adds trade route to repository'''
        name = self.__inputName.text()
        start = self.__inputStart.text()
        end = self.__inputEnd.text()

        if len(name) > 0 and len(start) > 0 and len(end) > 0:
            self.__presenter.onNewTradeRoute(name, start, end)
        else:
            print("Error! Not enough trade route parameters set!")

        self.__dialog.close()

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()