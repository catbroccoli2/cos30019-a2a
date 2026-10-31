"""The generic tree-search loop shared by DFS, BFS, GBFS and A*.

Conventions :

  * Search is TREE-based: there is no global explored set. The only repeat
    check is that a child may not revisit a node already on its own path
    (this stops cycles such as 1 <-> 3 from looping forever).
  * A node is CREATED when it is generated as a child during expansion and
    added to the frontier. The root counts as 1. Children skipped by the cycle
    check are never created, so they are not counted.
  * `number_of_nodes` in the output is the total number of nodes created.
  * The GOAL TEST is applied when a node is removed from the frontier
    (at expansion), not when it is generated. This keeps A* correct.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .frontier import Frontier
from .graph import Cost
from .problem import Problem
from .search_node import SearchNode


@dataclass
class SearchResult:
    """What a search method returns to the command-line front end."""

    goal: Optional[int]                 # destination reached, None if no path
    nodes_created: int                  # see conventions above
    path: List[int] = field(default_factory=list)   # origin ... goal
    cost: Optional[Cost] = None         # total path cost (for testing/reports)

    @property
    def found(self) -> bool:
        return self.goal is not None

    @classmethod
    def from_goal_node(cls, node: SearchNode, nodes_created: int) -> "SearchResult":
        """Build a successful result from the tree node that reached a goal."""
        return cls(goal=node.state, nodes_created=nodes_created,
                   path=node.path(), cost=node.path_cost)

    @classmethod
    def no_solution(cls, nodes_created: int) -> "SearchResult":
        return cls(goal=None, nodes_created=nodes_created)


class SearchSpace:
    """Creates and counts search-tree nodes for one run of one method.

    Every method (including the custom ones) should create nodes only through
    this class so that the node count and `order` stamps stay consistent.
    """

    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.nodes_created = 0

    def _new_node(self, state: int, parent: Optional[SearchNode], step_cost: Cost) -> SearchNode:
        # `order` is the number of nodes created before this one.
        node = SearchNode(
            state=state,
            parent=parent,
            path_cost=step_cost if parent is None else parent.path_cost + step_cost,
            depth=0 if parent is None else parent.depth + 1,
            order=self.nodes_created,
        )
        self.nodes_created += 1
        return node

    def create_root(self) -> SearchNode:
        """Create the root node for the problem's origin."""
        return self._new_node(self.problem.origin, None, 0)

    def expand(self, node: SearchNode) -> List[SearchNode]:
        """Generate the children of `node`.

        Children are returned in ascending node-number order (rule 1) with
        increasing `order` stamps (rule 2). Neighbours already on the current
        path are skipped.
        """
        children: List[SearchNode] = []
        for neighbour, cost in self.problem.graph.neighbours(node.state):
            if node.on_path(neighbour):
                continue
            children.append(self._new_node(neighbour, node, cost))
        return children


def run_search(problem: Problem, frontier: Frontier) -> SearchResult:
    """Run tree search with the given (empty) frontier and return the result.

    The strategy (DFS, BFS, GBFS, A*, ...) is decided entirely by which node
    `frontier.pop()` returns next.
    """
    space = SearchSpace(problem)
    frontier.push(space.create_root())

    while len(frontier) > 0:
        node = frontier.pop()
        if problem.is_goal(node.state):          # goal test at expansion
            return SearchResult.from_goal_node(node, space.nodes_created)
        frontier.extend(space.expand(node))

    return SearchResult.no_solution(space.nodes_created)
