import math
from typing import Generic, List, TypeVar


T = TypeVar('T')


class _kdtreenode(Generic[T]):

    def __init__(self, values: List[T], dimensions: int, depth: int) -> None:
        self.dimension = depth % dimensions
        self.value = None
        self._left = None
        self._right = None
        if not values:
            return

        values.sort(key=lambda el: el[self.dimension])
        split_index = len(values) // 2

        self.value = values[split_index]
        self._left = _kdtreenode(values[:split_index], dimensions, depth + 1)
        self._right = _kdtreenode(values[split_index + 1:], dimensions, depth + 1)

    def _swap_dimension(self):
        if self.dimension == 0:
            return 1
        else:
            return 0

    def __repr__(self):
        return f"value: {self.value}; dimension: {self.dimension}"

    def __iter__(self):
        if not self.value:
            return None

        yield self.value

        left_iter = iter(self._left or [])
        right_iter = iter(self._right or [])

        while True:
            next_left = next(left_iter, None)
            next_right = next(right_iter, None)
            if next_left:
                yield next_left

            if next_right:
                yield next_right

            if not any((next_left, next_right)):
                break

        return None

    def add(self, value: T, next_dimension: int):
        if value[self.dimension] <= self.value[self.dimension]:
            self._left = self._add_to_node(self._left, value, next_dimension)
        else:
            self._right = self._add_to_node(self._right, value, next_dimension)

    def nearest_to(self, search_value: T, best_node: '_kdtreenode', stack: List['_kdtreenode']) -> '_kdtreenode':
        stack.append(self)
        child = self._child_by_comparison(search_value)
        if child:
            return child.nearest_to(search_value, best_node, stack)

        return self._find_nearest_node(search_value, best_node, stack)

    def _find_nearest_node(self, search_value: T, best_node: '_kdtreenode', stack: List['_kdtreenode']):
        previous_node = None
        best_dist = self._dist(best_node.value, search_value)

        while stack:
            current_node = stack.pop()
            current_value = current_node.value or (math.inf, math.inf)
            current_dist = self._dist(current_value, search_value)
            dist_in_dimension = abs(current_value[current_node.dimension]
                                    - search_value[current_node.dimension])

            if current_dist <= best_dist:
                best_node = current_node
                best_dist = self._dist(best_node.value, search_value)

            if dist_in_dimension <= best_dist:
                best_node = self._find_nearest_in_other_branch(search_value, best_node,
                                                               previous_node, current_node)

            previous_node = current_node

        return best_node

    def _dist(self, a, b) -> float:
        if not all((a, b)):
            return (math.inf, math.inf)

        return math.dist(a, b)

    def _find_nearest_in_other_branch(self, search_value, best_node, previous_node, current_node):
        other_child = self._other_child(previous_node, current_node)
        if not other_child:
            return best_node

        return other_child.nearest_to(search_value,
                                      best_node, [])

    def _child_by_comparison(self, search_value: T) -> '_kdtreenode':
        if self._left and search_value[self.dimension] <= self.value[self.dimension]:
            return self._left

        if self._right and search_value[self.dimension] > self.value[self.dimension]:
            return self._right

        return None

    def _other_child(self, child, current_node: '_kdtreenode'):
        if child == current_node._left:
            other_child = current_node._right
        elif child == current_node._right:
            other_child = current_node._left
        else:
            raise ValueError("The child node was neither left nor right child")

        return other_child

    def _add_to_node(self, node, value, next_dimension):
        if node is None:
            node = _kdtreenode(value, next_dimension)
        else:
            node.add(value, next_dimension)

        return node


class kdtree(Generic[T]):

    def __init__(self, values: List[T]):
        self._root: _kdtreenode = None

        if values:
            dimensions = len(values[0])
            if not all(len(value) == dimensions for value in values):
                raise ValueError("All values must have the same dimension")

            self._root = _kdtreenode(values, dimensions, 0)

    def __iter__(self):
        if not self._root:
            return None

        for value in self._root:
            yield value

    # def add(self, value):
    #     if self._root is None:
    #         self._root = _kdtreenode(
    #             value, dimension=self._swap_dimension())
    #         return

    #     self._root.add(value, self._swap_dimension())

    def nearest_to(self, value: T) -> T:
        best_node = self._root
        if not self._root:
            raise TypeError("Tree does not have a root")

        return self._root.nearest_to(value, best_node, []).value
