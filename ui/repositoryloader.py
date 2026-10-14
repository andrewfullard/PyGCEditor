from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from threading import Event

from RepositoryCreator import RepositoryCreator
from gameObjects.gameObjectRepository import GameObjectRepository


class RepositoryLoader(QObject):
    """Builds a game-object repository outside the GUI thread."""

    loaded = pyqtSignal(object)
    failed = pyqtSignal(object)
    progress = pyqtSignal(str, int, int)

    def __init__(
        self,
        dataFolders,
        startingForcesLibraryURL: str,
        repositoryCreatorFactory=RepositoryCreator,
        cancellationEvent: Event | None = None,
    ) -> None:
        super().__init__()
        self.__dataFolders = dataFolders
        self.__startingForcesLibraryURL = startingForcesLibraryURL
        self.__repositoryCreatorFactory = repositoryCreatorFactory
        self.__cancellationEvent = cancellationEvent or Event()

    def load(self) -> None:
        try:
            repositoryCreator = self.__repositoryCreatorFactory()
            if hasattr(repositoryCreator, "setProgressCallback"):
                repositoryCreator.setProgressCallback(self.__reportProgress)
            repository = repositoryCreator.constructRepository(
                self.__dataFolders, self.__startingForcesLibraryURL
            )
        except Exception as error:
            self.failed.emit(error)
            return

        self.loaded.emit(repository)

    def cancel(self) -> None:
        self.__cancellationEvent.set()

    def __reportProgress(self, description: str, current: int, total: int) -> None:
        if self.__cancellationEvent.is_set():
            raise RuntimeError("Repository loading cancelled")
        self.progress.emit(description, current, total)


class RepositoryLoadResult(QObject):
    """Receives asynchronous repository loading results on the GUI thread."""

    def __init__(self, loadingLoop, loadingThread: QThread) -> None:
        super().__init__()
        self.repository: GameObjectRepository | None = None
        self.error: Exception | None = None
        self.__loadingLoop = loadingLoop
        self.__loadingThread = loadingThread

    @pyqtSlot(object)
    def setRepository(self, repository: GameObjectRepository) -> None:
        self.repository = repository
        self.__loadingThread.quit()
        self.__loadingLoop.quit()

    @pyqtSlot(object)
    def setError(self, error: Exception) -> None:
        self.error = error
        self.__loadingThread.quit()
        self.__loadingLoop.quit()