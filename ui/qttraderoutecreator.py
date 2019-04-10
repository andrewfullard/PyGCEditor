from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit

from gameObjects.traderoute import TradeRoute
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.qtautocomplete import AutoCompleter
from ui.dialogs import Dialog, DialogResult

class QtTradeRouteCreator(Dialog):
    '''Class for a "new trade route" dialog box'''
    def __init__(self, repository: GameObjectRepository):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__autoComplete = None

        self.__inputName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputStart: QLineEdit = QLineEdit(self.__dialog)
        self.__inputEnd: QLineEdit = QLineEdit(self.__dialog)

        self.__inputStart.textChanged.connect(self.__autoName)
        self.__inputEnd.textChanged.connect(self.__autoName)
      
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

        self.__result = DialogResult.Cancel

        self.__repository = repository

        self.__name = ""
        self.__start = None
        self.__end = None
        
       
    def show(self) -> DialogResult:
        '''Display dialog non-modally'''
        self.__setupAutoComplete()
        self.__dialog.exec()
        return self.__result

    def getCreatedTradeRoute(self) -> TradeRoute:
        '''Returns the created TradeRoute'''

        tradeRoute: TradeRoute = TradeRoute(self.__name)
        tradeRoute.start = self.__repository.getPlanetByName(self.__start)
        tradeRoute.end = self.__repository.getPlanetByName(self.__end)

        return tradeRoute      

    def __setupAutoComplete(self) -> None:
        '''Sets up autocompleter with planet names'''
        autoCompleter = AutoCompleter(self.__repository.getPlanetNames())
        planetCompleter = autoCompleter.completer()
        self.__inputStart.setCompleter(planetCompleter)
        self.__inputEnd.setCompleter(planetCompleter)

    def __autoName(self) -> None:
        '''Automatically names trade routes as start_end'''
        self.__inputName.setText(self.__inputStart.text() + "_" + self.__inputEnd.text())

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking and adds trade route to repository'''
        self.__name = self.__inputName.text()
        self.__start = self.__inputStart.text()
        self.__end = self.__inputEnd.text()

        if not self.__tradeRouteDataIsValid():
            print("Error! Not enough trade route parameters set!")
            return

        if self.__repository.tradeRouteExists(self.__start, self.__end):
            print("Error! Trade route already exists!")
            return

        self.__result = DialogResult.Ok
        self.__dialog.close()

    def __tradeRouteDataIsValid(self) -> bool:
        '''Checks if the trade route data is filled in and the planets exist in the repo'''
        return self.__name and self.__repository.planetExists(self.__start) and self.__repository.planetExists(self.__end)

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()