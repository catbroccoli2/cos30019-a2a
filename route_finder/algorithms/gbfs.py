"""Greedy Best-First Search (GBFS) - informed. Owner: Person B.

GBFS always expands the frontier node that LOOKS closest to a destination:

    f(n) = h(n) = straight-line distance from n to the nearest destination

It ignores the cost already paid (g), so it is usually fast but neither
optimal nor, in general, complete on infinite graphs. Here it is complete,
because the current-path cycle check makes the search tree finite.

Implementation: the generic tree search in `engine.run_search` with a
`PriorityFrontier` keyed on h(n). Ties on h are broken by lower node number,
then by earlier insertion into the frontier (the brief's two rules), entirely
inside `PriorityFrontier`.

Sample file (origin 2, destinations 5 and 4): goal 5, 6 nodes, 2 -> 3 -> 5.
"""

from __future__ import annotations

from ..engine import SearchResult, run_search
from ..frontier import PriorityFrontier
from ..heuristics import straight_line_heuristic
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    """Run greedy best-first tree search on `problem`."""
    h = straight_line_heuristic(problem)
    return run_search(problem, PriorityFrontier(lambda node: h(node.state)))
