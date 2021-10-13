from PyQt5.QtWidgets import QHeaderView, QTableWidget

class QtTableWidgetFactory():
    '''Factory for table widgets'''
    def __init__(self):
        pass
    
    def construct(self, label = ["Empty"], columns = 1) -> QTableWidget:
        '''Constructs an arbitrary table widget'''
        tableWidget: QTableWidget = QTableWidget()
        tableWidget.setColumnCount(columns)
        tableWidget.setHorizontalHeaderLabels(label)
        tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tableWidget.verticalHeader().setVisible(False)
        return tableWidget

    