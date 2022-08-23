from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QTableWidgetItem

from ui.qttablewidgetfactory import QtTableWidgetFactory

class QtPlanetsTradeRoutes(QWidget):
    campaignComboBoxSignal = pyqtSignal(int)
    campaignPropertiesButtonSignal = pyqtSignal(bool)

    planetListWidgetSignal = pyqtSignal(QTableWidgetItem)
    planetListWidgetContextSignal = pyqtSignal(int)
    tradeRouteListWidgetSignal = pyqtSignal(QTableWidgetItem)

    def __init__(self, parent: QWidget = None):
        super(QtPlanetsTradeRoutes, self).__init__()
        self.widget: QWidget = QWidget(parent)
        self.widget.setLayout(QVBoxLayout())

        self.__tableWidgetFactory = QtTableWidgetFactory()
        
        self.campaignComboBox: QComboBox = QComboBox()
        self.campaignPropertiesButton: QPushButton = QPushButton(
            "Campaign Properties"
        )
        
        self.planetCountLabel: QLabel = QLabel()

        self.planetListWidget = self.__tableWidgetFactory.construct(["Planets"])
        self.planetListWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.tradeRouteListWidget = self.__tableWidgetFactory.construct(["Trade Routes"])

        self.campaignComboBox.activated.connect(self.__onCampaignSelected)
        self.campaignPropertiesButton.clicked.connect(self.__campaignPropertiesButtonClicked)
        self.planetListWidget.customContextMenuRequested.connect(self.__showPlanetContextMenu)
        self.planetListWidget.itemClicked.connect(self.__onPlanetTableWidgetItemClicked)
        self.tradeRouteListWidget.itemClicked.connect(self.__onTradeRouteTableWidgetItemClicked)

        self.widget.layout().addWidget(self.campaignComboBox)
        self.widget.layout().addWidget(self.campaignPropertiesButton)
        self.widget.layout().addWidget(self.planetCountLabel)
        self.widget.layout().addWidget(self.planetListWidget)
        self.widget.layout().addWidget(self.tradeRouteListWidget)

    def __onCampaignSelected(self, event) -> None:
        '''Event handler for user choosing a campaign from dropdown'''
        self.campaignComboBoxSignal.emit(event)

    def __campaignPropertiesButtonClicked(self) -> bool:
        '''Event handler for user clicking the campaign properties button'''
        self.campaignPropertiesButtonSignal.emit(True)

    def __onPlanetTableWidgetItemClicked(self, event) -> None:
        '''Event handler for user clicking a planet entry'''
        self.planetListWidgetSignal.emit(event)

    def __onTradeRouteTableWidgetItemClicked(self, event) -> None:
        '''Event handler for user clicking a trade route entry'''
        self.tradeRouteListWidgetSignal.emit(event)

    def __showPlanetContextMenu(self, event) -> None:
        '''Event handler for user accessing the context menu for planets'''
        self.planetListWidgetContextSignal.emit(event)

    def empty(self) -> None:
        self.planetListWidget.clearContents()
        self.planetListWidget.setRowCount(0)
        self.tradeRouteListWidget.clearContents()
        self.tradeRouteListWidget.setRowCount(0)
        self.campaignComboBox.clear()