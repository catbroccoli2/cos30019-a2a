"""CUS1 - Iterative Deepening Depth-First Search (IDDFS), uninformed. Owner: Person C.

IDDFS runs a depth-limited DFS with limit 0, then 1, then 2, ... until a
destination is popped. Like BFS it reaches a goal with the FEWEST MOVES (not
necessarily the lowest cost); like DFS it only ever holds one branch of the
tree, so its frontier stays small.

How it fits the team conventions:

  * Nodes are created only through one `SearchSpace` that lives for the whole
    search, so `number_of_nodes` is CUMULATIVE: the root and any node that is
    re-generated in a later deepening round are counted again each time.
    (Confirm this choice with the team; it is the only place it is decided.)
  * Each round uses the shared `StackFrontier`, so children are expanded in
    ascending node order and branches are explored most-recent-first,
    exactly as in DFS.
  * The goal test happens when a node is popped.
  * Tree search with the usual current-path cycle check (inside
    `SearchSpace.expand`). That check also bounds every branch at |V| - 1
    moves, which is how we know when to give up.
"""

from __future__ import annotations

from typing import Optional, Tuple

from ..engine import SearchResult, SearchSpace
from ..frontier import StackFrontier
from ..problem import Problem
from ..search_node import SearchNode


def _has_unvisited_neighbour(problem: Problem, node: SearchNode) -> bool:
    """True if `node` could be expanded further, i.e. the depth limit hid something."""
    return any(not node.on_path(neighbour)
               for neighbour, _ in problem.graph.neighbours(node.state))


def _depth_limited_search(space: SearchSpace,
                          depth_limit: int) -> Tuple[Optional[SearchNode], bool]:
    """One DFS round that never expands a node deeper than `depth_limit`.

    Returns (goal node or None, whether the limit cut off part of the tree).
    """
    frontier = StackFrontier()
    frontier.push(space.create_root())
    cut_off = False
    while len(frontier) > 0:
        node = frontier.pop()
        if space.problem.is_goal(node.state):
            return node, cut_off
        if node.depth < depth_limit:
            frontier.extend(space.expand(node))
        elif _has_unvisited_neighbour(space.problem, node):
            cut_off = True
    return None, cut_off


def search(problem: Problem) -> SearchResult:
    """Run iterative-deepening depth-first tree search on `problem`."""
    space = SearchSpace(problem)
    # A branch without repeated nodes has at most |V| - 1 moves, so no deeper
    # round can find anything new.
    for depth_limit in range(len(problem.graph)):
        goal, cut_off = _depth_limited_search(space, depth_limit)
        if goal is not None:
            return SearchResult.from_goal_node(goal, space.nodes_created)
        if not cut_off:
            break  # the whole tree fitted under the limit and held no goal
    return SearchResult.no_solution(space.nodes_created)
