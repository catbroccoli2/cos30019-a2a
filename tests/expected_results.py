"""Hand-worked expected results for every problem file in tests/cases/. Owner: Person D.

Each answer was traced by hand from the team conventions (README.md) and the
rules in each algorithm's docstring BEFORE the program was run, so the test
suite checks the code against an independent calculation, not against itself.

Conventions used in the traces:
  * Tree search; a child never revisits a node on its own path.
  * "Nodes created" counts the root and every child generated, once each.
  * IDDFS (CUS1) and IDA* (CUS2) count nodes cumulatively over all rounds.
  * Goal test when a node is popped. Ties: lower node number, then earlier added.
  * GBFS and A* use straight-line distance to the nearest destination; CUS2 uses
    ceil(straight-line distance / longest edge length) as its move estimate.

Each answer is an `Expected`: (goal, nodes created, path, path cost).
`Expected(None, n, [], None)` means no destination is reachable after n nodes.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from route_finder.engine import SearchResult  # noqa: E402

METHOD_ORDER = ("DFS", "BFS", "GBFS", "AS", "CUS1", "CUS2")


class Expected(NamedTuple):
    """The hand-worked outcome of one method on one problem file."""

    goal: Optional[int]
    nodes: int
    path: List[int]
    cost: Optional[float]


class Case(NamedTuple):
    """One test case: its file, what it exercises and the expected results."""

    file: str
    title: str
    purpose: str
    expected: Dict[str, Expected]


def matches(result: SearchResult, expected: Expected) -> bool:
    """True if a search result equals the hand-worked answer (costs compared as numbers)."""
    if result.goal != expected.goal or result.nodes_created != expected.nodes:
        return False
    if result.path != expected.path:
        return False
    if expected.cost is None:
        return result.cost is None
    return result.cost is not None and math.isclose(result.cost, expected.cost, abs_tol=1e-9)


def found(goal: int, nodes: int, path: List[int], cost: float) -> Expected:
    """Expected outcome when the method reaches `goal`."""
    return Expected(goal, nodes, path, cost)


def missed(nodes: int) -> Expected:
    """Expected outcome when no destination can be reached."""
    return Expected(None, nodes, [], None)


def same_path(goal: int, path: List[int], cost: float, nodes: Dict[str, int]) -> Dict[str, Expected]:
    """Expected outcomes for methods that all return one path but count nodes differently."""
    return {method: found(goal, count, path, cost) for method, count in nodes.items()}


def counts(dfs: int, bfs: int, gbfs: int, astar: int, cus1: int, cus2: int) -> Dict[str, int]:
    """Node counts in METHOD_ORDER, labelled so the case table below stays readable."""
    return dict(zip(METHOD_ORDER, (dfs, bfs, gbfs, astar, cus1, cus2)))


CASES: List[Case] = [
    Case("PathFinder-test.txt", "Assignment sample",
         "The brief's own example with two destinations; A* has a genuine cost tie (10 vs 10).",
         {"DFS": found(5, 7, [2, 1, 3, 5], 15),
          "BFS": found(4, 10, [2, 1, 4], 10),
          "GBFS": found(5, 6, [2, 3, 5], 10),
          "AS": found(4, 8, [2, 1, 4], 10),
          "CUS1": found(4, 9, [2, 1, 4], 10),
          "CUS2": found(4, 5, [2, 1, 4], 10)}),

    Case("case02_chain.txt", "Single destination on a chain",
         "Simplest possible search: one path, so every method returns it; IDDFS repeats shallow work (1+2+3+4).",
         same_path(4, [1, 2, 3, 4], 3, counts(4, 4, 4, 4, 10, 4))),

    Case("case03_origin_is_destination.txt", "Origin is a destination",
         "The root is already a goal: one node, path of length zero, cost 0, for every method.",
         same_path(2, [2], 0, counts(1, 1, 1, 1, 1, 1))),

    Case("case04_two_destinations.txt", "Two destinations, different best choices",
         "Fewest moves reaches 3 (2 moves, cost 12) but the cheapest goal is 5 (3 moves, cost 3).",
         {"DFS": found(3, 4, [1, 2, 3], 12),
          "BFS": found(3, 5, [1, 2, 3], 12),
          "GBFS": found(5, 5, [1, 4, 6, 5], 3),
          "AS": found(5, 5, [1, 4, 6, 5], 3),
          "CUS1": found(3, 8, [1, 2, 3], 12),
          "CUS2": found(3, 7, [1, 2, 3], 12)}),

    Case("case05_unreachable_goal.txt", "Unreachable goal",
         "The destination has no edges at all; every method must exhaust the tree and report failure.",
         {"DFS": missed(3), "BFS": missed(3), "GBFS": missed(3), "AS": missed(3),
          "CUS1": missed(6), "CUS2": missed(3)}),

    Case("case06_disconnected_graph.txt", "Disconnected graph",
         "A second component holds destination 5; the search must still reach 3 in the origin's component.",
         same_path(3, [1, 2, 3], 4, counts(3, 3, 3, 3, 6, 3))),

    Case("case07_cycle.txt", "Cycle on the way to the goal",
         "Edge 3->1 closes a loop; the current-path check must stop the search going round it.",
         same_path(4, [1, 2, 3, 4], 7, counts(4, 4, 4, 4, 10, 6))),

    Case("case08_one_way_edges.txt", "One-way edge blocks a shortcut",
         "Edge 3->1 exists but 1->3 does not; a search that ignored direction would reach 3 in one move.",
         same_path(3, [1, 2, 3], 6, counts(3, 3, 3, 3, 6, 5))),

    Case("case09_dead_ends.txt", "Dead-end branch",
         "DFS and IDDFS enter the dead end 1->2->4 first and must back up to reach 5 through 3.",
         same_path(5, [1, 3, 5], 2, counts(5, 5, 4, 4, 9, 4))),

    Case("case10_tie_lower_node_first.txt", "Tie-break rule 1: lower node number",
         "Goals 3 and 5 are equally close and listed '5; 3'; node 3 must win because it is lower.",
         same_path(3, [1, 3], 3, counts(3, 3, 3, 3, 4, 3))),

    Case("case11_tie_earlier_added.txt", "Tie-break rule 2: earlier added",
         "Goal 4 appears twice with identical priority (via 2 and via 3); the copy added first must win.",
         same_path(4, [1, 2, 4], 6, counts(4, 5, 4, 5, 8, 4))),

    Case("case12_gbfs_suboptimal.txt", "GBFS is suboptimal, A* is optimal",
         "GBFS follows the straight-line lure 1-2-5 (cost 20); A* finds 1-3-4-5 (cost 8).",
         {"DFS": found(5, 4, [1, 2, 5], 20),
          "BFS": found(5, 5, [1, 2, 5], 20),
          "GBFS": found(5, 4, [1, 2, 5], 20),
          "AS": found(5, 5, [1, 3, 4, 5], 8),
          "CUS1": found(5, 8, [1, 2, 5], 20),
          "CUS2": found(5, 4, [1, 2, 5], 20)}),

    Case("case13_inadmissible_heuristic.txt", "Inadmissible heuristic",
         "Edges 1->3 and 3->4 cost less than their length, so h overestimates and A* returns "
         "cost 8 although 1-3-4 costs 4. Documents A*'s limit when the heuristic is not admissible.",
         same_path(4, [1, 2, 4], 8, counts(4, 5, 4, 4, 8, 4))),

    Case("case14_larger_graph_22_nodes.txt", "Larger graph (22 nodes)",
         "A spine with 10 pendant leaves; the goal is leaf 13, so DFS wanders the whole spine first.",
         same_path(13, [1, 2, 13], 2, counts(22, 6, 4, 4, 7, 4))),

    Case("case15_dense_graph.txt", "Dense graph (complete, 5 nodes)",
         "Every node links to every other; A* ties on f=4 across all monotone paths and creates 21 nodes.",
         {"DFS": found(5, 11, [1, 2, 3, 4, 5], 4),
          "BFS": found(5, 14, [1, 5], 4),
          "GBFS": found(5, 5, [1, 5], 4),
          "AS": found(5, 21, [1, 5], 4),
          "CUS1": found(5, 6, [1, 5], 4),
          "CUS2": found(5, 5, [1, 5], 4)}),

    Case("case16_decimal_values.txt", "Decimal coordinates and costs",
         "Costs 2.5 and 3.5 and coordinates such as (0.5,0.5): the parser and the totals must stay exact.",
         {"DFS": found(4, 5, [1, 2, 3, 4], 7.5),
          "BFS": found(4, 6, [1, 3, 4], 6.0),
          "GBFS": found(4, 4, [1, 3, 4], 6.0),
          "AS": found(4, 5, [1, 3, 4], 6.0),
          "CUS1": found(4, 9, [1, 3, 4], 6.0),
          "CUS2": found(4, 5, [1, 3, 4], 6.0)}),

    Case("case17_numeric_node_order.txt", "Numeric (not text) node order",
         "Children 9 and 10: sorted as text '10' would come first; numerically 9 must be expanded first.",
         same_path(20, [5, 9, 20], 6, counts(4, 5, 4, 5, 8, 4))),

    Case("case18_isolated_origin.txt", "Origin with no outgoing edges",
         "The root has no children, so every method stops after exactly one node.",
         {method: missed(1) for method in METHOD_ORDER}),

    Case("case19_self_loop_duplicate_edge.txt", "Self-loops and a duplicate edge",
         "Self-loops (1,1) and (2,2) must be ignored; edge (1,2) is listed twice and the cheaper (2) is kept.",
         same_path(3, [1, 2, 3], 4, counts(3, 3, 3, 3, 6, 3))),

    Case("case20_many_destinations.txt", "Every other node is a destination",
         "Four destinations all one move away; the lowest numbered (1) must be chosen.",
         same_path(1, [3, 1], 2, counts(5, 5, 5, 5, 6, 5))),
]
