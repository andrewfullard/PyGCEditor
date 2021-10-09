import math
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np
import numpy.linalg as linalg
from gameObjects.planet import Planet
from gameObjects.traderoute import TradeRoute
from graph.kdtree import kdtree

from PyQt5.QtCore import QPoint, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen, QResizeEvent, QWheelEvent
from PyQt5.QtWidgets import QWidget

from ui.galacticplot import GalacticPlot


class CoordinateSystem:

    def __init__(self) -> None:
        self._top_left = (0, 0)
        self._bottom_right = (0, 0)
        self._middle = (0, 0)

    @property
    def bounds(self):
        return self._top_left, self._bottom_right

    @bounds.setter
    def bounds(self, value):
        self._top_left, self._bottom_right = value[0], value[1]
        self._calc_middle()

    @property
    def middle(self):
        return self._middle

    def _calc_middle(self):
        mid_x = (self._top_left[0] + self._bottom_right[0]) / 2
        mid_y = (self._top_left[1] + self._bottom_right[1]) / 2
        self._middle = (mid_x, mid_y)


class CoordinateTransformer:

    def __init__(self) -> None:
        self.view = CoordinateSystem()
        self.world = CoordinateSystem()

        self._trans_matrix = []
        self._inv_trans_matrix = []

    def transformation_matrix(self):
        s = self.scale_factor()
        tx = self.view.middle[0] - self.world.middle[0]
        ty = self.view.middle[1] - self.world.middle[1]

        negative_world_mid = (-self.world.middle[0], -self.world.middle[1])
        trans_matrix = np.matmul(self.translation(*negative_world_mid), self.scaling(s))
        trans_matrix = np.matmul(trans_matrix, self.translation(*self.world.middle))
        trans_matrix = np.matmul(trans_matrix, self.translation(tx, ty))

        self._trans_matrix = trans_matrix
        self._inv_trans_matrix = linalg.inv(self._trans_matrix)

    def translation(self, tx, ty):
        return np.array([
            [1, 0, 0],
            [0, 1, 0],
            [tx, ty, 1]
        ])

    def scaling(self, s):
        return np.array([
            [s, 0, 0],
            [0, -s, 0],
            [0, 0, 1]
        ])

    def scale_factor(self):
        vx = abs((self.view.bounds[0][0] - self.view.bounds[1][0]) /
                 (self.world.bounds[0][0] - self.world.bounds[1][0]))

        vy = abs((self.view.bounds[0][1] - self.view.bounds[1][1]) /
                 (self.world.bounds[0][1] - self.world.bounds[1][1]))

        return min(vx, vy)

    def to_view_point(self, point) -> Tuple[int, int]:
        point_matrix = np.matmul(
            np.array([point[0], point[1], 1]), self._trans_matrix)

        return (int(point_matrix[0]), int(point_matrix[1]))

    def to_world_point(self, point) -> Tuple[int, int]:
        point_matrix = np.matmul(
            np.array([point[0], point[1], 1]), self._inv_trans_matrix)

        return (point_matrix[0], point_matrix[1])

    def to_view_length(self, length):
        return int(self.scale_factor() * length)

    def to_world_length(self, length):
        return length / self.scale_factor()

    def zoom(self, factor: float, x: int, y: int):
        zoom = 1 - factor
        wx, wy = self.to_world_point((x, y))
        dx = wx * factor
        dy = wy * factor

        current_bounds = self.world.bounds
        self.world.bounds = (
            (current_bounds[0][0] * zoom + dx, current_bounds[0][1] * zoom + dy),
            (current_bounds[1][0] * zoom + dx, current_bounds[1][1] * zoom + dy),
        )

        self.transformation_matrix()



@dataclass
class PlotPlanet:
    x: int
    y: int
    planet: Planet = field(compare=False)
    index: int = field(compare=False)

    @classmethod
    def from_planet(cls, planet: Planet, index: int):
        return PlotPlanet(planet.x, planet.y, planet, index)

    def __getitem__(self, index: int):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y

        raise IndexError

    def __len__(self):
        return 2


class BetterQtGalacticPlot(QWidget):

    planetSelectedSignal = pyqtSignal(list)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setMinimumSize(500, 500)
        self._size = self.size()
        self.setMouseTracking(True)

        self._transformer = CoordinateTransformer()

        self._tree: kdtree[PlotPlanet] = None
        self._planets: List[Planet] = []
        self._traderoutes: List[TradeRoute] = []
        self._nearest = None
        self._first_paint = True
        self._world_planet_radius = 10


    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        view_dist = self._find_nearest_and_get_view_dist(event)
        if view_dist <= 10:
            self.planetSelectedSignal.emit([self._nearest.index])

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        view_dist = self._find_nearest_and_get_view_dist(event)
        if view_dist <= 10:
            self.repaint(self.rect())

    def wheelEvent(self, event: QWheelEvent) -> None:
        dy = event.angleDelta().y()
        dir = 1 if dy >= 0 else -1
        self._transformer.zoom(dir * 0.1, event.x(), event.y())
        self.repaint()

    def _find_nearest_and_get_view_dist(self, event):
        if not self._tree:
            return math.inf

        point = self._transformer.to_world_point((event.x(), event.y()))
        self._nearest = self._tree.nearest_to(point)
        return self._transformer.to_view_length(math.dist(point, self._nearest))

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._update_view_bounds_and_transformation_matrix()
        self.repaint()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        self.plotPlanets(self._planets, painter)
        self.plotTradeRoutes(self._traderoutes, painter)
        painter.end()

    def plotGalaxy(self, planets: List[Planet], tradeRoutes: List[TradeRoute], all_planets: List[Planet], autoconnect_distance: float) -> None:
        min_x, max_x = math.inf, -math.inf
        min_y, max_y = math.inf, -math.inf

        self._planets = planets
        self._traderoutes = tradeRoutes
        if not self._planets:
            self._tree = None
            self._nearest = None
            self.repaint()
            return

        planets_with_index = []
        planet_set = set(planets)
        for index, planet in enumerate(all_planets):
            min_x, max_x = (min(planet.x or min_x, min_x),
                            max(planet.x or max_x, max_x))
            min_y, max_y = (min(planet.y or min_y, min_y),
                            max(planet.y or max_y, max_y))

            if planet in planet_set and all((planet.x, planet.y)):
                planets_with_index.append((planet, index))

        self._nearest = None
        self._tree = kdtree([PlotPlanet.from_planet(planet, index)
                             for planet, index in planets_with_index])


        self._update_world_bounds_on_first_paint(min_x, max_x, min_y, max_y)
        self._update_view_bounds_and_transformation_matrix()
        

        self.repaint()

    def _update_world_bounds_on_first_paint(self, min_x, max_x, min_y, max_y):
        if not self._first_paint:
            return
        
        self._first_paint = False
        self._transformer.world.bounds = ((min_x, max_y), (max_x, min_y))

    def _update_view_bounds_and_transformation_matrix(self):
        size = self.size()
        dx, dy = size.width() * .1, size.height() * .1
        self._transformer.view.bounds = ((dx, dy), (size.width() * .9, size.height() * .9))
        self._transformer.transformation_matrix()

    def plotPlanets(self, planets: List[Planet], painter: QPainter) -> None:
        pen = painter.pen()
        pen.setWidth(10)
        painter.setPen(pen)

        view_planet_radius = self._transformer.to_view_length(self._world_planet_radius)
        for planet in planets:
            coords = (planet.x, planet.y)
            if not all(coords):
                continue

            viewpoint = self._transformer.to_view_point(coords)
            if self._nearest and self._nearest.planet == planet:
                pen.setBrush(Qt.GlobalColor.red)
                painter.setPen(pen)

            painter.drawEllipse(QPoint(*viewpoint), view_planet_radius, view_planet_radius)
            pen.setBrush(Qt.GlobalColor.black)
            painter.setPen(pen)

    def plotTradeRoutes(self, tradeRoutes: List[TradeRoute], painter: QPainter) -> None:
        pen = painter.pen()
        pen.setWidth(1)
        painter.setPen(pen)
        for route in tradeRoutes:
            start = (route.start.x, route.start.y)
            end = (route.end.x, route.end.y)

            if not (all(start) and all(end)):
                continue

            view_start = self._transformer.to_view_point(start)
            view_end = self._transformer.to_view_point(end)

            painter.drawLine(*view_start, *view_end)
