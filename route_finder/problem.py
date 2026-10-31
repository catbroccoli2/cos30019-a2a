"""A Route Finding problem: a graph, an origin and a set of destinations."""

from __future__ import annotations

from typing import Iterable, Tuple

from .graph import Graph


class Problem:
    """Everything a search method needs to know about one problem file."""

    def __init__(self, graph: Graph, origin: int, destinations: Iterable[int]) -> None:
        self.graph = graph
        self.origin = origin
        # Keep the file's order for display; use a set for fast goal tests.
        self.destinations: Tuple[int, ...] = tuple(destinations)
        self._goal_set = frozenset(self.destinations)

    def is_goal(self, state: int) -> bool:
        """True if `state` is one of the destination nodes."""
        return state in self._goal_set
