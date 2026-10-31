"""Public entry point of the research feature: visit ALL destinations, shortest walk.

Steps: (1) Dijkstra gives the shortest distance between every pair of
{origin, destinations}; (2) an exact solver picks the best visiting order;
(3) the shortest routes between consecutive stops are joined into one walk.
Joining shortest routes is enough because an optimal walk never gains by
leaving a shortest route between two stops, and a destination that lies on
such a route is visited on the way at no extra cost.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Set

from route_finder.graph import Cost
from route_finder.problem import Problem

from .distances import INFINITY, PairwiseDistances
from .orderings import best_order_by_dp, best_order_by_permutations, best_walk_by_state_search

SOLVERS = ("auto", "perm", "dp", "ucs")
# 'auto' enumerates permutations up to this many destinations (8! = 40,320
# orders is instant), then switches to the DP.
PERMUTATION_LIMIT = 8
# The DP table has 2^k * k entries; beyond 16 destinations it gets too large.
DP_LIMIT = 16


@dataclass
class TourResult:
    """Outcome of one run of the research feature."""

    reachable: bool
    solver: str
    cost: Cost = 0
    walk: List[int] = field(default_factory=list)          # every node entered, origin first
    visit_order: List[int] = field(default_factory=list)   # destinations in first-reached order
    unreachable: List[int] = field(default_factory=list)   # destinations the origin cannot reach


def _first_visits(walk: Iterable[int], destinations: Set[int]) -> List[int]:
    """Destinations in the order the walk first reaches them."""
    seen: List[int] = []
    for node in walk:
        if node in destinations and node not in seen:
            seen.append(node)
    return seen


def visit_all(problem: Problem, solver: str = "auto") -> TourResult:
    """Find the cheapest walk from the origin that reaches every destination.

    `solver` is one of SOLVERS. Raises ValueError for an unknown solver or for
    more than DP_LIMIT destinations with a table-based solver.
    """
    if solver not in SOLVERS:
        raise ValueError(f"unknown solver {solver!r}; choose from {', '.join(SOLVERS)}")
    destinations = set(problem.destinations)

    if solver == "ucs":
        cost, walk, _ = best_walk_by_state_search(problem)
        if cost == INFINITY:
            return TourResult(False, solver)
        return TourResult(True, solver, cost, walk, _first_visits(walk, destinations))

    table = PairwiseDistances(problem)
    unreachable = [d for d in table.destinations if table.distance(table.origin, d) == INFINITY]
    if unreachable:
        return TourResult(False, solver, unreachable=unreachable)

    count = len(table.destinations)
    if solver == "auto":
        solver = "perm" if count <= PERMUTATION_LIMIT else "dp"
    if solver == "dp" and count > DP_LIMIT:
        raise ValueError(f"{count} destinations is too many for the DP (limit {DP_LIMIT}); "
                         "use the 'ucs' solver or fewer destinations")
    choose_order = best_order_by_permutations if solver == "perm" else best_order_by_dp
    cost, order = choose_order(table)
    if cost == INFINITY:  # every destination is reachable from the origin, but not from each other
        return TourResult(False, solver)

    walk = [table.origin]
    for source, target in zip((table.origin,) + order, order):
        walk.extend(table.path(source, target)[1:])  # [1:] drops the repeated junction node
    return TourResult(True, solver, cost, walk, _first_visits(walk, destinations))
