"""The search-tree node used by every search method."""

from __future__ import annotations

from typing import List, Optional

from .graph import Cost


class SearchNode:
    """One node of the search tree.

    Attributes:
        state:     the graph node this tree node represents.
        parent:    the tree node it was generated from (None for the root).
        path_cost: g(n), the total edge cost from the origin to this node.
        depth:     number of moves from the origin.
        order:     creation number (0 for the root, then 1, 2, ...). Because a
                   node is added to the frontier the moment it is created,
                   this is also its chronological position for tie-break rule 2.
    """

    __slots__ = ("state", "parent", "path_cost", "depth", "order")

    def __init__(self, state: int, parent: Optional["SearchNode"],
                 path_cost: Cost, depth: int, order: int) -> None:
        self.state = state
        self.parent = parent
        self.path_cost = path_cost
        self.depth = depth
        self.order = order

    def path(self) -> List[int]:
        """The graph nodes from the origin to this node, in order."""
        states: List[int] = []
        node: Optional[SearchNode] = self
        while node is not None:
            states.append(node.state)
            node = node.parent
        states.reverse()
        return states

    def on_path(self, state: int) -> bool:
        """True if `state` is this node or one of its ancestors.

        Used for cycle checking along the CURRENT path only (the assignment's
        search is tree-based, so there is no global explored set).
        """
        node: Optional[SearchNode] = self
        while node is not None:
            if node.state == state:
                return True
            node = node.parent
        return False

    def __repr__(self) -> str:
        return f"SearchNode(state={self.state}, g={self.path_cost}, order={self.order})"
