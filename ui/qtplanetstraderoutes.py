from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QTableWidget

from ui.qttablewidgetfactory import QtTableWidgetFactory

class QtPlanetsTradeRoutes(object):
    def __init__(self):
        self.widget: QWidget = QWidget()
        self.widget.setLayout(QVBoxLayout())

        self.__tableWidgetFactory = QtTableWidgetFactory()
        
        self.campaignComboBox: QComboBox = QComboBox()
        self.campaignPropertiesButton: QPushButton = QPushButton(
            "Campaign Properties"
        )
        self.selectAllPlanetsButton: QPushButton = QPushButton("Select All Planets")
        self.deselectAllPlanetsButton: QPushButton = QPushButton(
            "Deselect All Planets"
        )
        
        self.planetCountLabel: QLabel = QLabel()

        self.planetListWidget = self.__tableWidgetFactory.construct(["Planets"])
        self.planetListWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.tradeRouteListWidget = self.__tableWidgetFactory.construct(["Trade Routes"])

        self.selectAllTradeRoutesButton: QPushButton = QPushButton("Select All Trade Routes")
        self.deselectAllTradeRoutesButton: QPushButton = QPushButton("Deselect All Trade Routes")

        self.widget.layout().addWidget(self.campaignComboBox)
        self.widget.layout().addWidget(self.campaignPropertiesButton)
        self.widget.layout().addWidget(self.planetCountLabel)
        self.widget.layout().addWidget(self.planetListWidget)
        self.widget.layout().addWidget(self.selectAllPlanetsButton)
        self.widget.layout().addWidget(self.deselectAllPlanetsButton)
        self.widget.layout().addWidget(self.tradeRouteListWidget)
        self.widget.layout().addWidget(self.selectAllTradeRoutesButton)
        self.widget.layout().addWidget(self.deselectAllTradeRoutesButton)

    def empty(self) -> None:
        self.planetListWidget.clearContents()
        self.planetListWidget.setRowCount(0)
        self.tradeRouteListWidget.clearContents()
        self.tradeRouteListWidget.setRowCount(0)
        self.campaignComboBox.clear()