"""Greedy Best-First Search (GBFS) - informed. Owner: Person B.

TODO (Person B): replace the body of `search` below.

Evaluation function: f(n) = h(n) only (ignores the cost so far).

Hints
-----
* Put your heuristic in a new file `route_finder/heuristics.py`, e.g.
  Euclidean distance from a node's coordinates to the NEAREST destination
  (get coordinates with `problem.graph.coordinates(node_id)`).
* Reuse the shared framework - it already does tie-breaking and node counting:

      from ..engine import run_search
      from ..frontier import PriorityFrontier
      ...
      return run_search(problem, PriorityFrontier(lambda n: h(problem, n.state)))

  `PriorityFrontier` breaks ties by lower node number, then by earlier
  insertion, exactly as the brief requires. Do not write your own ordering.
"""

from __future__ import annotations

from ..engine import SearchResult
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    raise NotImplementedError("GBFS is not implemented yet (Person B).")
