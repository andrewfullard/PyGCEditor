import sys

from PyQt5.QtWidgets import QApplication

from config import Config
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.qtmainwindow import QtMainWindow

config: config = Config()

numArgs = len(sys.argv)

if numArgs > 1:
    path = sys.argv[1]
else:
    path = config.dataPath

app = QApplication([])

qtMainWindow: QtMainWindow = QtMainWindow()
presenter: MainWindowPresenter = MainWindowPresenter(qtMainWindow, path)
qtMainWindow.setMainWindowPresenter(presenter)
qtMainWindow.getWindow().show()

app.exec_()
