"""CUS2 - custom INFORMED search. Owner: Person B.

TODO (Person B): replace the body of `search` below.

Requirement from the brief: an informed method that finds a shortest path
(LEAST MOVES) to the goal. Confirm your choice with the tutor (IDA* or A* on
hop count are the usual picks).

Hints
-----
* "Shortest" here means fewest edges, so g(n) is `node.depth`, not
  `node.path_cost`.
* The heuristic must not overestimate the number of moves. Euclidean distance
  divided by the longest edge length, rounded up, is a safe lower bound.
* Create nodes ONLY through `SearchSpace` so counting and ordering stay
  consistent with the other methods.
"""

from __future__ import annotations

from ..engine import SearchResult
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    raise NotImplementedError("CUS2 is not implemented yet (Person B).")
