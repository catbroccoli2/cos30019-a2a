"""Breadth-First Search (BFS) - uninformed. Owner: Person A.

BFS expands every node at depth d before any node at depth d + 1, so the goal
it returns is reached with the FEWEST MOVES (not necessarily the lowest cost,
because edge costs differ).

Implementation: the generic tree search in `engine.run_search` with a FIFO
`QueueFrontier`. Children are enqueued in ascending node order (tie-break
rule 1); the queue gives chronological order between branches (rule 2).
"""

from __future__ import annotations

from ..engine import SearchResult, run_search
from ..frontier import QueueFrontier
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    """Run breadth-first tree search on `problem`."""
    return run_search(problem, QueueFrontier())
