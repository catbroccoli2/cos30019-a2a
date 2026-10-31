"""A* Search (AS) - informed. Owner: Person B.

A* expands the frontier node with the lowest estimated total cost:

    f(n) = g(n) + h(n)

where g(n) is the cost of the path so far (`node.path_cost`) and h(n) is the
straight-line distance from n to the nearest destination.

Optimality: the goal test happens when a node is popped (see engine.py), and
h never overestimates when every edge costs at least its straight-line length
(checked with `heuristics.underestimated_edges`). Under that condition the
first goal popped is a lowest-cost path. The sample file satisfies it.

Ties on f are broken by lower node number, then by earlier insertion into the
frontier, inside `PriorityFrontier`.

Sample file: 2 -> 3 -> 5 and 2 -> 1 -> 4 both cost 10, so f = 10 for both
goal nodes. Rule 1 picks node 4: goal 4, 8 nodes, 2 -> 1 -> 4.
"""

from __future__ import annotations

from ..engine import SearchResult, run_search
from ..frontier import PriorityFrontier
from ..heuristics import straight_line_heuristic
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    """Run A* tree search on `problem`."""
    h = straight_line_heuristic(problem)
    return run_search(problem, PriorityFrontier(lambda node: node.path_cost + h(node.state)))
