"""Registry mapping each command-line method name to its search function.

Every algorithm module exposes `search(problem) -> SearchResult`.
To add or swap a method, change only this table.
"""

from __future__ import annotations

from typing import Callable, Dict

from ..engine import SearchResult
from ..problem import Problem
from . import astar, bfs, cus1, cus2, dfs, gbfs

METHODS: Dict[str, Callable[[Problem], SearchResult]] = {
    "DFS": dfs.search,
    "BFS": bfs.search,
    "GBFS": gbfs.search,
    "AS": astar.search,
    "CUS1": cus1.search,
    "CUS2": cus2.search,
}
