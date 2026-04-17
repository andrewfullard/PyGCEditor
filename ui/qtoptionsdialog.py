from typing import List

from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QFormLayout,
)

from ui.dialogs import Dialog, DialogResult


class QtOptionsDialog(Dialog):
    """Dialog for modifying config.xml settings."""

    def __init__(self):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__modPathInput: QLineEdit = QLineEdit(self.__dialog)
        self.__submodsInput: QTextEdit = QTextEdit(self.__dialog)
        self.__autoConnectionDistanceInput: QLineEdit = QLineEdit(self.__dialog)
        self.__startingForcesLibraryURLInput: QLineEdit = QLineEdit(self.__dialog)

        submodHelpText = QLabel(
            "Enter one submod per line in ascending priority order."
        )

        self.__okButton: QPushButton = QPushButton("OK")
        self.__okButton.clicked.connect(self.__okayClicked)

        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("Mod Path", self.__modPathInput)
        self.__formLayout.addRow("Submods", self.__submodsInput)
        self.__formLayout.addRow("", submodHelpText)
        self.__formLayout.addRow(
            "Maximum Fleet Movement Distance", self.__autoConnectionDistanceInput
        )
        self.__formLayout.addRow(
            "Starting Forces Library URL", self.__startingForcesLibraryURLInput
        )

        self.__buttonLayout.addWidget(self.__okButton)
        self.__buttonLayout.addWidget(self.__cancelButton)

        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("Options")
        self.__dialog.setLayout(self.__layout)
        self.__dialog.resize(600, 350)

        self.__result = DialogResult.Cancel

        self.__modPath = ""
        self.__submods: List[str] = []
        self.__autoConnectionDistance = 0
        self.__startingForcesLibraryURL = ""

    def show(
        self,
        modPath: str,
        submods: List[str],
        autoConnectionDistance: int,
        startingForcesLibraryURL: str,
    ) -> DialogResult:
        """Display dialog modally."""
        self.__modPathInput.setText(modPath)
        self.__submodsInput.setPlainText("\n".join(submods))
        self.__autoConnectionDistanceInput.setText(str(autoConnectionDistance))
        self.__startingForcesLibraryURLInput.setText(startingForcesLibraryURL)

        self.__dialog.exec()
        return self.__result

    def getModPath(self) -> str:
        return self.__modPath

    def getSubmods(self) -> List[str]:
        return self.__submods

    def getAutoConnectionDistance(self) -> int:
        return self.__autoConnectionDistance

    def getStartingForcesLibraryURL(self) -> str:
        return self.__startingForcesLibraryURL

    def __okayClicked(self) -> None:
        try:
            distance = int(self.__autoConnectionDistanceInput.text().strip())
            if distance < 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(
                self.__dialog,
                "Invalid Value",
                "Maximum Fleet Movement Distance must be a non-negative integer.",
            )
            return

        self.__modPath = self.__modPathInput.text().strip()
        self.__submods = [
            line.strip()
            for line in self.__submodsInput.toPlainText().splitlines()
            if line.strip()
        ]
        self.__autoConnectionDistance = distance
        self.__startingForcesLibraryURL = (
            self.__startingForcesLibraryURLInput.text().strip()
        )

        self.__result = DialogResult.Ok
        self.__dialog.close()

    def __cancelClicked(self) -> None:
        self.__dialog.close()
