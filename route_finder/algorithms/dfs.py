"""Depth-First Search (DFS) - uninformed. Owner: Person A.

DFS always expands the most recently generated node, so it follows one branch
as deep as it can before backing up ("select one option, try it, go back when
there are no more options").

Implementation: the generic tree search in `engine.run_search` with a LIFO
`StackFrontier`. Children are pushed in reverse order so the lowest-numbered
child is expanded first (tie-break rule 1). Cycles are prevented by the
current-path check in `SearchSpace.expand`.

DFS is not optimal and does not minimise cost or moves.
"""

from __future__ import annotations

from ..engine import SearchResult, run_search
from ..frontier import StackFrontier
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    """Run depth-first tree search on `problem`."""
    return run_search(problem, StackFrontier())
