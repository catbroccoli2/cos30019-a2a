"""CUS2 - custom INFORMED search: IDA* on move count. Owner: Person B.

Goal (from the brief): an informed method that finds a shortest path to a
destination, where "shortest" means the FEWEST MOVES (edges), not lowest cost.

Method: Iterative-Deepening A* (IDA*) with

    g(n) = number of moves so far          (`node.depth`)
    h(n) = ceil(straight-line distance to nearest destination / longest edge length)
    f(n) = g(n) + h(n)

Each iteration is a depth-first search that prunes (does not expand) any node
whose f exceeds the current bound. The first bound is f(root); each later
bound is the smallest f that was pruned in the previous iteration. Because h
never overestimates the moves left, the first destination found is reached in
the fewest possible moves. The search stops with no solution when an
iteration prunes nothing, which always happens because the current-path cycle
check makes the search tree finite.

Why IDA* rather than A* on depth: it is clearly a different algorithm from
our AS (depth-first inside a bound, memory linear in the path length), and
it is the standard memory-efficient optimal informed search.

Conventions (same as the other methods):
  * Tree search with the current-path cycle check (SearchSpace.expand).
  * Goal test when a node is popped.
  * Tie-breaking: within an iteration this is depth-first, so children are
    expanded in ascending node-number order (rule 1, via StackFrontier).
  * `number_of_nodes` is the TOTAL created over ALL iterations, because
    every iteration really does generate its nodes again. The root of each
    iteration is counted too.

Sample file: goal 4, 5 nodes, 2 -> 1 -> 4 (bound 2 is enough on the first
iteration; 2 -> 1 -> 4 and 2 -> 3 -> 5 are both 2 moves and node 1's branch
is explored first).
"""

from __future__ import annotations

from typing import Callable, Optional, Tuple

from ..engine import SearchResult, SearchSpace
from ..frontier import StackFrontier
from ..heuristics import move_count_heuristic
from ..problem import Problem


def search(problem: Problem) -> SearchResult:
    """Run IDA* (fewest moves) tree search on `problem`."""
    h = move_count_heuristic(problem)
    space = SearchSpace(problem)      # shared by all iterations, so counts accumulate
    bound: Optional[int] = h(problem.origin)

    while bound is not None:
        result, bound = _bounded_depth_first(problem, space, h, bound)
        if result is not None:
            return result

    return SearchResult.no_solution(space.nodes_created)


def _bounded_depth_first(problem: Problem, space: SearchSpace, h: Callable[[int], int],
                         bound: int) -> Tuple[Optional[SearchResult], Optional[int]]:
    """One IDA* iteration: depth-first search that skips nodes with f > bound.

    Returns (result, None) if a destination is found, otherwise
    (None, next_bound), where next_bound is the smallest f that was pruned,
    or None if nothing was pruned (the whole tree was searched: no solution).
    """
    frontier = StackFrontier()
    frontier.push(space.create_root())
    next_bound: Optional[int] = None

    while len(frontier) > 0:
        node = frontier.pop()
        f = node.depth + h(node.state)
        if f > bound:
            if next_bound is None or f < next_bound:
                next_bound = f
            continue
        if problem.is_goal(node.state):          # goal test at expansion
            return SearchResult.from_goal_node(node, space.nodes_created), None
        frontier.extend(space.expand(node))

    return None, next_bound
