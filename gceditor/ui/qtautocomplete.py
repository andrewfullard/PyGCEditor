from typing import List

from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import QStringListModel

class AutoCompleter:
    '''Set up an autocomplete addon for text entry using an input list'''
    def __init__(self, autoCompleteList):
        self.__completer: QCompleter = QCompleter()
        self.__list: List[str] = autoCompleteList

    def setupModel(self, model):
        '''Creates an autocompleter model'''
        model.setStringList(self.__list)
    
    def completer(self):
        '''Produces the completer'''
        model = QStringListModel()
        self.__completer.setModel(model)
        self.setupModel(model)
        return self.__completer