"""Frontier data structures.

A search method is defined by *which node it removes from the frontier next*.
All of the assignment's tie-breaking rules are implemented in this file:

  Rule 1  When all else is equal, the lower-numbered node is expanded first.
  Rule 2  When two nodes on different branches are still tied, the one that
          was added to the frontier earlier is expanded first.

Children always arrive from `SearchSpace.expand` already sorted by ascending
node number and already stamped with increasing `order` values.
"""

from __future__ import annotations

import heapq
from abc import ABC, abstractmethod
from collections import deque
from typing import Callable, Deque, Iterable, List, Tuple

from .search_node import SearchNode

# Heuristic values are floats (square roots). Rounding them before comparing
# stops tiny floating-point noise (10.000000000000002 vs 10.0) from breaking
# what should be an exact tie.
PRIORITY_DECIMALS = 9


class Frontier(ABC):
    """The set of tree nodes that have been generated but not yet expanded."""

    @abstractmethod
    def push(self, node: SearchNode) -> None:
        """Add one node."""

    @abstractmethod
    def pop(self) -> SearchNode:
        """Remove and return the next node to expand."""

    @abstractmethod
    def __len__(self) -> int:
        ...

    def extend(self, children: Iterable[SearchNode]) -> None:
        """Add the children of one expansion (given in ascending node order)."""
        for child in children:
            self.push(child)


class StackFrontier(Frontier):
    """LIFO frontier, used by DFS.

    Children are pushed in REVERSE order so the lowest-numbered child ends up
    on top of the stack and is expanded first (rule 1). Between branches, the
    most recently added node is expanded first, which is what makes it DFS.
    """

    def __init__(self) -> None:
        self._items: List[SearchNode] = []

    def push(self, node: SearchNode) -> None:
        self._items.append(node)

    def extend(self, children: Iterable[SearchNode]) -> None:
        for child in reversed(list(children)):
            self._items.append(child)

    def pop(self) -> SearchNode:
        return self._items.pop()

    def __len__(self) -> int:
        return len(self._items)


class QueueFrontier(Frontier):
    """FIFO frontier, used by BFS.

    Children are enqueued in ascending order (rule 1) and the queue itself
    gives chronological order between branches (rule 2).
    """

    def __init__(self) -> None:
        self._items: Deque[SearchNode] = deque()

    def push(self, node: SearchNode) -> None:
        self._items.append(node)

    def pop(self) -> SearchNode:
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)


class PriorityFrontier(Frontier):
    """Priority-queue frontier for informed / cost-ordered searches.

    Pass a function that maps a SearchNode to its priority (smaller = sooner):
        GBFS -> h(n)        A* -> g(n) + h(n)        UCS -> g(n)
    Ties are broken by the full key (priority, node number, creation order),
    which implements rule 1 and then rule 2.
    """

    def __init__(self, priority: Callable[[SearchNode], float]) -> None:
        self._priority = priority
        self._heap: List[Tuple[Tuple[float, int, int], SearchNode]] = []

    def push(self, node: SearchNode) -> None:
        key = (round(self._priority(node), PRIORITY_DECIMALS), node.state, node.order)
        # `order` is unique per node, so two keys are never equal and the heap
        # never has to compare SearchNode objects.
        heapq.heappush(self._heap, (key, node))

    def pop(self) -> SearchNode:
        return heapq.heappop(self._heap)[1]

    def __len__(self) -> int:
        return len(self._heap)
