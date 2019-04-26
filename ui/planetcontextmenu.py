from PyQt5.QtWidgets import QMenu

from ui.dialogs import Dialog, DialogResult
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.planetpositionchanger import PlanetPositionChanger


class PlanetContextMenu():
    ''' A context menu that appears on right clicking a planet in the list '''
    def __init__(self, presenter: MainWindowPresenter):
        self.__menu: QMenu = QMenu()
        self.__changePositionAction = self.__menu.addAction("Change position")
        self.__presenter = presenter

        self.__dialog = None


    def show(self, item, position) -> None:

        choice = self.__menu.exec_(position)

        ''' Shows the "change coordinates" dialog '''
        if choice is self.__changePositionAction:
            name = self.__presenter.getNameOfPlanetAt(item.row())
            old_x, old_y = self.__presenter.getPositionOfPlanetAt(item.row())
            self.__dialog: PlanetPositionChanger = PlanetPositionChanger(self.__presenter, name, old_x, old_y)
            result: DialogResult = self.__dialog.show()
            if result is DialogResult.Ok:
                x,y = self.__dialog.getNewCoordinates()
                self.__presenter.onPlanetPositionChanged(name, x, y)

