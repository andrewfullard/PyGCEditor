#from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit

from gameObjects.planet import Planet
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtautocomplete import AutoCompleter
from ui.dialogs import Dialog, DialogResult

class PlanetPositionChanger(Dialog):
    '''Class for a "change planet position" dialog box'''
    def __init__(self, presenter: MainWindowPresenter, planet_name, old_x, old_y):
        self.__presenter = presenter
        self.__planet_name = planet_name
        self.__old_x = old_x
        self.__old_y = old_y

        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__inputX: QLineEdit = QLineEdit(self.__dialog)
        self.__inputX.setText(str(self.__old_x))
        self.__inputY: QLineEdit = QLineEdit(self.__dialog)
        self.__inputY.setText(str(self.__old_y))

        #self.__inputX.textChanged.connect(self.__autoName)
        #self.__inputY.textChanged.connect(self.__autoName)

        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)

        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("X coordinate", self.__inputX)
        self.__formLayout.addRow("Y coordinate", self.__inputY)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)

        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("Adjust position of " + self.__planet_name)
        self.__dialog.setLayout(self.__layout)

        self.__presenter = None

        self.__result = DialogResult.Cancel

        self.__x = None
        self.__y = None


    def show(self) -> DialogResult:
        '''Display dialog non-modally'''
        self.__dialog.exec()
        return self.__result

    def getNewCoordinates(self):
        '''Returns the new coordinates'''
        return self.__x, self.__y

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking'''
        try:
            self.__x = float(self.__inputX.text())
            self.__y = float(self.__inputY.text())
        except ValueError:
            print("Error! Wrong coordinate format. X: ", self.__x, "Y: ", self.__y)
            self.__dialog.close()
            return

        self.__result = DialogResult.Ok
        self.__dialog.close()

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()