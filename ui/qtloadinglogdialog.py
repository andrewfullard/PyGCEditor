import logging

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QDialog, QLabel, QPlainTextEdit, QProgressBar, QVBoxLayout


class QtLoadingLogDialog(QDialog):
    """Displays application loading progress and log records."""

    loadingCancelled = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Loading Galactic Conquest Editor")
        self.resize(720, 360)

        layout = QVBoxLayout(self)
        self.__statusLabel = QLabel("Loading...")
        self.__modPathLabel = QLabel()
        self.__submodsLabel = QLabel()
        self.__startingforcesLabel = QLabel()
        self.__progressBar = QProgressBar()
        self.__progressBar.setRange(0, 0)
        self.__logOutput = QPlainTextEdit()
        self.__logOutput.setReadOnly(True)
        self.__loading = False

        layout.addWidget(self.__statusLabel)
        layout.addWidget(self.__modPathLabel)
        layout.addWidget(self.__submodsLabel)
        layout.addWidget(self.__startingforcesLabel)
        layout.addWidget(self.__progressBar)
        layout.addWidget(self.__logOutput)

    def beginLoading(self) -> None:
        self.__loading = True
        self.__statusLabel.setText("Loading...")
        self.__progressBar.setRange(0, 0)
        self.show()
        self.repaint()

    def setLoadingPaths(self, modPath: str, submods: list[str], startingForcesLibrary: str) -> None:
        self.__modPathLabel.setText(f"Mod path: {modPath}")
        submodText = ", ".join(submods) if submods else "None"
        self.__submodsLabel.setText(f"Submods: {submodText}")
        self.__startingforcesLabel.setText(f"Starting Forces Library: {startingForcesLibrary}")

    def getModPathLabel(self) -> str:
        return self.__modPathLabel.text()

    def getSubmodsLabel(self) -> str:
        return self.__submodsLabel.text()

    def completeLoading(self) -> None:
        self.__loading = False
        self.__statusLabel.setText("Loading complete")
        self.__progressBar.setRange(0, 1)
        self.__progressBar.setValue(1)
        self.hide()

    def updateProgress(self, description: str, current: int, total: int) -> None:
        self.__statusLabel.setText(description)
        if total > 0:
            self.__progressBar.setRange(0, total)
            self.__progressBar.setValue(current)
        else:
            self.__progressBar.setRange(0, 0)

    def showLog(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def appendLogRecord(self, record: logging.LogRecord) -> None:
        self.__logOutput.appendPlainText(
            f"{record.levelname}: {record.getMessage()}"
        )

    def closeEvent(self, event) -> None:
        if self.__loading:
            self.loadingCancelled.emit()
        event.accept()


class QtLogHandler(QObject, logging.Handler):
    """Forwards Python log records to the loading dialog."""

    recordEmitted = pyqtSignal(object)

    def __init__(self, dialog: QtLoadingLogDialog) -> None:
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.recordEmitted.connect(dialog.appendLogRecord)

    def emit(self, record: logging.LogRecord) -> None:
        self.recordEmitted.emit(record)
