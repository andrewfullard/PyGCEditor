from abc import ABC, abstractmethod
from typing import Any
from PyQt6.QtWidgets import QGridLayout, QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

class FormWidget(ABC):

    @abstractmethod
    def getContent(self) -> Any:
        pass

    @abstractmethod
    def getWidget(self) -> QWidget:
        pass


class Form(QWidget):

    onConfirm: pyqtSignal = pyqtSignal()
    onCancel: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__inputFields = {}
        self.__ok = QPushButton("Ok")
        self.__cancel = QPushButton("Cancel")

        self.__ok.clicked.connect(self.__onConfirm)
        self.__cancel.clicked.connect(self.__onCancel)

        self.setLayout(QGridLayout())
        self.__rows = 0


    def __onConfirm(self) -> None:
        self.onConfirm.emit()

    def __onCancel(self) -> None:
        self.onCancel.emit()

    def show(self):
        buttonBar = QWidget()
        buttonBar.setLayout(QHBoxLayout())
        buttonBar.layout().addWidget(self.__ok)
        buttonBar.layout().addWidget(self.__cancel)
        self.layout().addWidget(buttonBar, self.__rows, 0, 1, -1)
        super().show()

    def addWidget(self, label: str, formWidget: FormWidget):
        self.__inputFields[label] = formWidget
        self.layout().addWidget(QLabel(label), self.__rows, 0)
        self.layout().addWidget(formWidget.getWidget(), self.__rows, 1)
        self.__rows += 1

    def getContent(self, label: str) -> Any:
        return self.__inputFields[label].getContent()


class TextWidget(FormWidget):

    def __init__(self):
        self.__widget: QLineEdit = QLineEdit()
    
    def getContent(self) -> str:
        return self.__widget.text()

    def getWidget(self) -> QWidget:
        return self.__widget


class FormBuilder:

    def __init__(self):
        self.__form = None

    def form(self):
        self.__form: QWidget = Form()

        return self

    def add_input(self, label: str, input_type: str):
        if input_type == "str":
            self.__form.addWidget(label, TextWidget())
        
        return self

    def finish(self) -> Form:
        return self.__form
