from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QTableWidgetItem

from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from ui.dialogs import Dialog, DialogResult
from ui.qttablewidgetfactory import QtTableWidgetFactory

class QtPlanetFileHider(Dialog):
    '''Class for a "change planet position" dialog box'''
    def __init__(self, presenter: MainWindowPresenter):
        self.__presenter = presenter

        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__fileListWidget: QtTableWidgetFactory = QtTableWidgetFactory().construct(["Show planet from:"])
        #self.__fileListWidget.itemClicked.connect(self.__onFileTableItemClicked)

        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)

        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)

        self.__layout.addWidget(self.__fileListWidget)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("Choose files from which to show planets")
        self.__dialog.setLayout(self.__layout)

        self.__presenter = None

        self.__result = DialogResult.Cancel
        
        self.__hiddenFileList = []
        self.__fileTableItems = []


    def show(self, fileList, hiddenFileList = []) -> DialogResult:
        '''Display dialog non-modally'''
        
        for fileName in fileList:
            rowCount = self.__fileListWidget.rowCount()
            self.__fileListWidget.setRowCount(rowCount + 1)
            item: QTableWidgetItem = QTableWidgetItem(fileName)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            if fileName in hiddenFileList:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)
            self.__fileTableItems.append(item)
            
            self.__fileListWidget.setItem(rowCount, 0, item)
        self.__dialog.exec()
        return self.__result

    def getHiddenFiles(self):
        '''Returns the hidden files'''
        return self.__hiddenFileList

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking'''
        for fileItem in self.__fileTableItems:
            if fileItem.checkState() == QtCore.Qt.Unchecked:
                self.__hiddenFileList.append(fileItem.text())
        self.__result = DialogResult.Ok
        self.__dialog.close()

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()