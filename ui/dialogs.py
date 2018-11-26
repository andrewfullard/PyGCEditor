from abc import ABC, abstractmethod
from enum import Enum

class DialogResult(Enum):

    Ok = 0
    Cancel = 1


class Dialog(ABC):

    @abstractmethod
    def show(self) -> DialogResult:
        raise NotImplementedError

