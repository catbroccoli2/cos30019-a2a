"""Shortest-path distances between the origin and the destinations.

The graph is directed, so the distance from a to b can differ from the
distance from b to a; every table here keeps both directions.
"""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Tuple

from route_finder.graph import Cost
from route_finder.problem import Problem

INFINITY = math.inf


def shortest_paths_from(problem: Problem, source: int) -> Tuple[Dict[int, Cost], Dict[int, int]]:
    """Dijkstra from `source`: returns (distance to each reachable node, predecessor map)."""
    distance: Dict[int, Cost] = {source: 0}
    predecessor: Dict[int, int] = {}
    heap: List[Tuple[Cost, int]] = [(0, source)]
    while heap:
        dist, node = heapq.heappop(heap)
        if dist > distance[node]:
            continue  # stale heap entry: a shorter route was already found
        for neighbour, cost in problem.graph.neighbours(node):
            candidate = dist + cost
            if candidate < distance.get(neighbour, INFINITY):
                distance[neighbour] = candidate
                predecessor[neighbour] = node
                heapq.heappush(heap, (candidate, neighbour))
    return distance, predecessor


class PairwiseDistances:
    """Shortest distances and paths between the origin and every destination.

    `points` lists the origin first, then the other destinations in ascending
    node order. Destinations equal to the origin or repeated in the file are
    dropped: they are visited for free at the start.
    """

    def __init__(self, problem: Problem) -> None:
        destinations = sorted(set(problem.destinations) - {problem.origin})
        self.points: List[int] = [problem.origin] + destinations
        self._distance: Dict[int, Dict[int, Cost]] = {}
        self._predecessor: Dict[int, Dict[int, int]] = {}
        for point in self.points:
            self._distance[point], self._predecessor[point] = shortest_paths_from(problem, point)

    @property
    def origin(self) -> int:
        return self.points[0]

    @property
    def destinations(self) -> List[int]:
        return self.points[1:]

    def distance(self, source: int, target: int) -> Cost:
        """Shortest distance source -> target (INFINITY if there is no route)."""
        return self._distance[source].get(target, INFINITY)

    def path(self, source: int, target: int) -> List[int]:
        """Nodes of one shortest route source -> target. Only call if it exists."""
        route = [target]
        while route[-1] != source:
            route.append(self._predecessor[source][route[-1]])
        route.reverse()
        return route
