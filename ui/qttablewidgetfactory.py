from PyQt6.QtWidgets import QHeaderView, QTableWidget

class QtTableWidgetFactory():
    '''Factory for table widgets'''
    def __init__(self):
        pass
    
    def construct(self, label = ["Empty"], columns = 1, stretch = True) -> QTableWidget:
        '''Constructs an arbitrary table widget'''
        tableWidget: QTableWidget = QTableWidget()
        tableWidget.setColumnCount(columns)
        tableWidget.setHorizontalHeaderLabels(label)
        
        if stretch:
            tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        else:
            tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        tableWidget.verticalHeader().setVisible(False)
        tableWidget.setSortingEnabled(True)
        return tableWidget

    