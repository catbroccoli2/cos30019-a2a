"""CUS1 - custom UNINFORMED search. Owner: Person C.

TODO (Person C): replace the body of `search` below.

Requirement from the brief: an uninformed method that finds a path to a goal.
Confirm your choice with the tutor (Iterative Deepening DFS and Uniform Cost
Search are the usual picks).

Hints
-----
* Create nodes ONLY through `SearchSpace` (`create_root`, `expand`) so the
  node count and the tie-breaking order stay consistent with the other methods.
* Uniform Cost Search fits the shared loop directly:
      return run_search(problem, PriorityFrontier(lambda n: n.path_cost))
* Iterative deepening needs its own loop (depth limit 0, 1, 2, ...). Decide
  and document whether `number_of_nodes` accumulates across iterations.
"""

from __future__ import annotations

from ..engine import SearchResult
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    raise NotImplementedError("CUS1 is not implemented yet (Person C).")
