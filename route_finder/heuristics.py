"""Heuristic functions for the informed searches (GBFS, A*, CUS2). Owner: Person B.

Two heuristics are provided, both built once per problem and cached per node:

* `straight_line_heuristic(problem)` - h(n) = Euclidean (straight-line)
  distance from n to the NEAREST destination. Used by GBFS and A*, which
  estimate remaining path COST.

* `move_count_heuristic(problem)` - h(n) = ceil(straight-line distance to the
  nearest destination / longest edge length). Used by CUS2, which estimates
  the remaining number of MOVES (edges).

Admissibility
-------------
Straight-line distance never overestimates the remaining cost as long as no
edge costs LESS than the straight-line length between its end points (the
triangle inequality then bounds every path from below). Edges may cost more
(the sample's 1 -> 3 is 3 units long but costs 5); that only makes h less
tight, never wrong. `underestimated_edges` lists any edge that breaks the
condition so a test file can be checked before trusting A*'s answer.

The move-count heuristic is always admissible: one move covers at most the
longest edge's straight-line length, so reaching a destination that is D
units away needs at least ceil(D / longest) moves, whatever the edge costs.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

from .graph import Cost, Graph
from .problem import Problem

# Same tolerance the PriorityFrontier uses. Rounding before `ceil` stops
# floating-point noise (2.0000000000000004) turning an exact 2 into 3, which
# would make the move-count heuristic overestimate.
_DECIMALS = 9


def euclidean_distance(graph: Graph, a: int, b: int) -> float:
    """Straight-line distance between the coordinates of nodes a and b."""
    ax, ay = graph.coordinates(a)
    bx, by = graph.coordinates(b)
    return math.hypot(ax - bx, ay - by)


def distance_to_nearest_destination(problem: Problem, state: int) -> float:
    """Straight-line distance from `state` to the closest destination (0 at a goal)."""
    return min(euclidean_distance(problem.graph, state, goal)
               for goal in problem.destinations)


def longest_edge_length(graph: Graph) -> float:
    """The largest straight-line length of any edge (0.0 if there are no edges)."""
    return max((euclidean_distance(graph, source, target)
                for source in graph.node_ids()
                for target, _ in graph.neighbours(source)),
               default=0.0)


def straight_line_heuristic(problem: Problem) -> Callable[[int], float]:
    """h(n) for GBFS and A*: straight-line distance to the nearest destination."""
    table: Dict[int, float] = {
        state: distance_to_nearest_destination(problem, state)
        for state in problem.graph.node_ids()
    }
    return table.__getitem__


def move_count_heuristic(problem: Problem) -> Callable[[int], int]:
    """h(n) for CUS2: a lower bound on the number of moves to the nearest destination."""
    longest = longest_edge_length(problem.graph)
    table: Dict[int, int] = {}
    for state in problem.graph.node_ids():
        distance = distance_to_nearest_destination(problem, state)
        if longest == 0:
            # No edge has any length (or there are no edges), so geometry
            # gives no information. 0 is the only safe estimate.
            table[state] = 0
        else:
            table[state] = math.ceil(round(distance / longest, _DECIMALS))
    return table.__getitem__


def underestimated_edges(graph: Graph) -> List[Tuple[int, int, Cost, float]]:
    """Edges whose cost is less than their straight-line length.

    Returns (source, target, cost, length) tuples. An empty list means the
    straight-line heuristic is consistent, and therefore admissible, on this
    graph, so A* is guaranteed to return a lowest-cost path.
    """
    bad: List[Tuple[int, int, Cost, float]] = []
    for source in graph.node_ids():
        for target, cost in graph.neighbours(source):
            length = euclidean_distance(graph, source, target)
            if round(cost - length, _DECIMALS) < 0:
                bad.append((source, target, cost, length))
    return bad
