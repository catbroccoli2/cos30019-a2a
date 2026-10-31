"""A* Search (AS) - informed. Owner: Person B.

TODO (Person B): replace the body of `search` below.

Evaluation function: f(n) = g(n) + h(n), where g(n) is `node.path_cost`.

Hints
-----
* Reuse the heuristic from `route_finder/heuristics.py` (shared with GBFS).
* Reuse the shared framework:

      return run_search(problem, PriorityFrontier(lambda n: n.path_cost + h(problem, n.state)))

* Check admissibility: an edge's cost can be larger than the straight-line
  distance between its end points, which is fine, but it must never be
  SMALLER, otherwise Euclidean distance can overestimate and A* may not be
  optimal. Check this on the sample file and mention it in the report.
* The sample file has a genuine tie (2->3->5 and 2->1->4 both cost 10); the
  tie-break rules decide the answer, so this is a good test case.
"""

from __future__ import annotations

from ..engine import SearchResult
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    raise NotImplementedError("AS (A*) is not implemented yet (Person B).")
