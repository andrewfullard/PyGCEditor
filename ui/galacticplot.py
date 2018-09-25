from abc import ABC, abstractmethod
from typing import List

from gameObjects.planet import Planet


class GalacticPlot(ABC):

    @abstractmethod
    def plotPlanets(self, planets: List[Planet]) -> None:
        raise NotImplementedError()
