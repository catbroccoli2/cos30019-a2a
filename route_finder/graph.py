"""Graph model for the Route Finding problem.

The graph is *directed*: an edge (a, b) lets the agent travel from a to b,
but not from b to a unless the edge (b, a) is also present.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

# Edge costs may be whole numbers or decimals.
Cost = Union[int, float]


@dataclass(frozen=True)
class Node:
    """A graph node and its 2D coordinates (used by informed searches)."""

    node_id: int
    x: float
    y: float


class Graph:
    """A directed graph with non-negative edge costs."""

    def __init__(self) -> None:
        self._nodes: Dict[int, Node] = {}
        # _edges[a][b] = cost of travelling a -> b
        self._edges: Dict[int, Dict[int, Cost]] = {}
        # Cache of neighbours sorted by node id (tie-break rule 1).
        self._sorted_neighbours: Dict[int, Tuple[Tuple[int, Cost], ...]] = {}

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def add_node(self, node_id: int, x: float, y: float) -> None:
        """Add a node. Raises ValueError if the id is already used."""
        if node_id in self._nodes:
            raise ValueError(f"node {node_id} is defined more than once")
        self._nodes[node_id] = Node(node_id, x, y)
        self._edges[node_id] = {}

    def add_edge(self, source: int, target: int, cost: Cost) -> None:
        """Add the directed edge source -> target.

        Raises ValueError for unknown nodes or a negative cost. If the same
        edge is listed twice, the cheaper cost is kept.
        """
        if source not in self._nodes:
            raise ValueError(f"edge ({source},{target}) uses undefined node {source}")
        if target not in self._nodes:
            raise ValueError(f"edge ({source},{target}) uses undefined node {target}")
        if cost < 0:
            raise ValueError(f"edge ({source},{target}) has a negative cost")
        existing = self._edges[source].get(target)
        if existing is None or cost < existing:
            self._edges[source][target] = cost
            self._sorted_neighbours.pop(source, None)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def has_node(self, node_id: int) -> bool:
        return node_id in self._nodes

    def node_ids(self) -> List[int]:
        """All node ids in ascending order."""
        return sorted(self._nodes)

    def coordinates(self, node_id: int) -> Tuple[float, float]:
        """The (x, y) coordinates of a node."""
        node = self._nodes[node_id]
        return node.x, node.y

    def neighbours(self, node_id: int) -> Tuple[Tuple[int, Cost], ...]:
        """Outgoing edges of a node as (neighbour_id, cost) pairs.

        Pairs are sorted by ascending neighbour id, so every search generates
        children in the order required by tie-break rule 1.
        """
        cached = self._sorted_neighbours.get(node_id)
        if cached is None:
            cached = tuple(sorted(self._edges[node_id].items()))
            self._sorted_neighbours[node_id] = cached
        return cached

    def edge_cost(self, source: int, target: int) -> Cost:
        """Cost of the edge source -> target (KeyError if it does not exist)."""
        return self._edges[source][target]

    def __len__(self) -> int:
        return len(self._nodes)
