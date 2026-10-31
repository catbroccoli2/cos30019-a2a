"""Unit tests for Person B's code: heuristics, GBFS, A* (AS) and CUS2 (IDA*).

Run from the repository root:
    python -m unittest discover -s tests -v
"""

import heapq
import random
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from route_finder.algorithms import astar, bfs, cus2, gbfs  # noqa: E402
from route_finder.heuristics import (  # noqa: E402
    euclidean_distance, longest_edge_length, move_count_heuristic,
    straight_line_heuristic, underestimated_edges)
from route_finder.parser import parse_problem_file, parse_problem_text  # noqa: E402

SAMPLE = ROOT / "tests" / "cases" / "PathFinder-test.txt"
INFORMED = (gbfs, astar, cus2)


def build(nodes, edges, origin, destinations):
    """Problem from {id: (x, y)}, [(a, b, cost)], origin, [destinations]."""
    lines = ["Nodes:"] + [f"{n}: ({x},{y})" for n, (x, y) in nodes.items()]
    lines += ["Edges:"] + [f"({a},{b}): {c}" for a, b, c in edges]
    lines += ["Origin:", str(origin), "Destinations:", "; ".join(map(str, destinations))]
    return parse_problem_text("\n".join(lines))


# Diamond 1 -> {2, 3} -> 4 -> 5. Node 3's branch is cheaper to reach, so its
# copy of node 4 joins the frontier FIRST; both copies of 4 then have the same
# f. Rule 2 says the earlier copy (via 3) must be expanded first.
RULE2_NODES = {1: (0, 0), 2: (0.5, 0.5), 3: (0.5, -0.5), 4: (1, 0), 5: (2, 0)}
RULE2_EDGES = [(1, 2, 2), (1, 3, 1), (2, 4, 1), (3, 4, 2), (4, 5, 1)]


class HeuristicTests(unittest.TestCase):
    def setUp(self):
        self.problem = parse_problem_file(SAMPLE)

    def test_straight_line_to_nearest_destination(self):
        h = straight_line_heuristic(self.problem)
        self.assertEqual(h(4), 0)
        self.assertEqual(h(5), 0)
        self.assertAlmostEqual(h(2), 17 ** 0.5)      # (2,2) -> node 4 at (6,3)
        self.assertAlmostEqual(h(3), 5 ** 0.5)       # (4,4) is equidistant from 4 and 5

    def test_sample_heuristic_is_admissible(self):
        self.assertEqual(underestimated_edges(self.problem.graph), [])

    def test_underestimated_edge_is_reported(self):
        problem = build({1: (0, 0), 2: (3, 4)}, [(1, 2, 2)], 1, [2])
        self.assertEqual(underestimated_edges(problem.graph), [(1, 2, 2, 5.0)])

    def test_move_count_heuristic(self):
        h = move_count_heuristic(self.problem)
        self.assertAlmostEqual(longest_edge_length(self.problem.graph), 10 ** 0.5)
        self.assertEqual([h(n) for n in range(1, 7)], [1, 2, 1, 0, 0, 1])

    def test_move_count_rounds_float_noise_down(self):
        # Exactly 2 edge-lengths away must give 2, not 3 from 2.0000000000000004.
        problem = build({1: (0, 0), 2: (0.1, 0), 3: (0.2, 0)}, [(1, 2, 1), (2, 3, 1)], 1, [3])
        self.assertEqual(move_count_heuristic(problem)(1), 2)

    def test_move_count_with_no_edges_is_zero(self):
        problem = build({1: (0, 0), 2: (5, 5)}, [], 1, [2])
        self.assertEqual(move_count_heuristic(problem)(1), 0)


class SampleFileTests(unittest.TestCase):
    """The targets agreed with the team for tests/cases/PathFinder-test.txt."""

    def setUp(self):
        self.problem = parse_problem_file(SAMPLE)

    def check(self, module, goal, nodes, path):
        result = module.search(self.problem)
        self.assertEqual((result.goal, result.nodes_created, result.path), (goal, nodes, path))

    def test_gbfs(self):
        self.check(gbfs, 5, 6, [2, 3, 5])

    def test_astar_tie_resolved_by_lower_node_number(self):
        # 2-3-5 and 2-1-4 both cost 10; rule 1 picks goal 4.
        self.check(astar, 4, 8, [2, 1, 4])
        self.assertEqual(astar.search(self.problem).cost, 10)

    def test_cus2(self):
        self.check(cus2, 4, 5, [2, 1, 4])


class TieBreakTests(unittest.TestCase):
    def test_rule1_equal_priority_lower_node_first(self):
        # 2 and 3 are mirror images: same h, same g. Node 2 must win.
        nodes = {1: (0, 0), 2: (1, 1), 3: (1, -1), 4: (2, 0)}
        edges = [(1, 3, 2), (1, 2, 2), (3, 4, 2), (2, 4, 2)]
        problem = build(nodes, edges, 1, [4])
        for module in INFORMED:
            with self.subTest(method=module.__name__):
                self.assertEqual(module.search(problem).path, [1, 2, 4])

    def test_rule2_astar_same_node_earlier_copy_first(self):
        result = astar.search(build(RULE2_NODES, RULE2_EDGES, 1, [5]))
        self.assertEqual(result.path, [1, 3, 4, 5])
        self.assertEqual(result.nodes_created, 7)

    def test_gbfs_ignores_cost_on_rule2_graph(self):
        # h(2) == h(3), so GBFS takes node 2 by rule 1 even though it costs more.
        result = gbfs.search(build(RULE2_NODES, RULE2_EDGES, 1, [5]))
        self.assertEqual(result.path, [1, 2, 4, 5])


class BehaviourTests(unittest.TestCase):
    def test_gbfs_greedy_vs_astar_optimal(self):
        # Node 2 is right next to the goal but its edge to it is expensive.
        nodes = {1: (0, 0), 2: (4, 0), 3: (2, 3), 4: (5, 0)}
        edges = [(1, 2, 4), (2, 4, 20), (1, 3, 4), (3, 4, 5)]
        problem = build(nodes, edges, 1, [4])
        self.assertEqual(gbfs.search(problem).path, [1, 2, 4])
        self.assertEqual(gbfs.search(problem).cost, 24)
        self.assertEqual(astar.search(problem).path, [1, 3, 4])
        self.assertEqual(astar.search(problem).cost, 9)

    def test_cus2_fewest_moves_not_cheapest(self):
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (3, 0)}
        edges = [(1, 2, 1), (2, 3, 1), (3, 4, 1), (1, 4, 100)]
        problem = build(nodes, edges, 1, [4])
        self.assertEqual(cus2.search(problem).path, [1, 4])
        self.assertEqual(astar.search(problem).path, [1, 2, 3, 4])

    def test_origin_is_destination(self):
        problem = build({1: (0, 0), 2: (1, 0)}, [(1, 2, 1)], 1, [1, 2])
        for module in INFORMED:
            with self.subTest(method=module.__name__):
                result = module.search(problem)
                self.assertEqual((result.goal, result.nodes_created, result.path), (1, 1, [1]))

    def test_unreachable_with_cycle_terminates(self):
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (9, 9)}
        edges = [(1, 2, 1), (2, 1, 1), (2, 3, 1), (3, 1, 2), (4, 1, 1)]   # 4 has no way in
        problem = build(nodes, edges, 1, [4])
        for module in INFORMED:
            with self.subTest(method=module.__name__):
                result = module.search(problem)
                self.assertFalse(result.found)
                self.assertGreater(result.nodes_created, 1)

    def test_cus2_counts_nodes_across_iterations(self):
        # Line 1 -> 2 -> 3 with a long side edge making h(1) = 1 < 2 moves needed.
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (0, 5)}
        edges = [(1, 2, 1), (2, 3, 1), (1, 4, 5)]
        result = cus2.search(build(nodes, edges, 1, [3]))
        # Bound 1: 1, 2, 4 created (3 nodes). Bound 2: 1, 2, 4, 3 (4 nodes).
        self.assertEqual((result.path, result.nodes_created), ([1, 2, 3], 7))


class RandomGraphTests(unittest.TestCase):
    """Compare against independent reference answers on many random graphs."""

    @staticmethod
    def random_problem(rng):
        count = rng.randint(2, 12)
        nodes = {n: (rng.randint(0, 9), rng.randint(0, 9)) for n in range(1, count + 1)}
        problem = build(nodes, [], 1, [1])
        edges = []
        for a in nodes:
            for b in nodes:
                if a != b and rng.random() < 0.3:
                    # Cost >= straight-line length keeps the heuristic admissible.
                    length = euclidean_distance(problem.graph, a, b)
                    edges.append((a, b, int(length) + 1 + rng.randint(0, 4)))
        goals = rng.sample(sorted(nodes), rng.randint(1, min(3, count)))
        return build(nodes, edges, rng.randint(1, count), goals)

    @staticmethod
    def cheapest_cost(problem):
        """Dijkstra from the origin to the nearest destination (None if unreachable)."""
        best = {problem.origin: 0}
        queue = [(0, problem.origin)]
        while queue:
            cost, state = heapq.heappop(queue)
            if problem.is_goal(state):
                return cost
            if cost > best[state]:
                continue
            for neighbour, step in problem.graph.neighbours(state):
                if cost + step < best.get(neighbour, float("inf")):
                    best[neighbour] = cost + step
                    heapq.heappush(queue, (cost + step, neighbour))
        return None

    @staticmethod
    def fewest_moves(problem):
        """Graph BFS from the origin to the nearest destination (None if unreachable)."""
        depth = {problem.origin: 0}
        queue = deque([problem.origin])
        while queue:
            state = queue.popleft()
            if problem.is_goal(state):
                return depth[state]
            for neighbour, _ in problem.graph.neighbours(state):
                if neighbour not in depth:
                    depth[neighbour] = depth[state] + 1
                    queue.append(neighbour)
        return None

    def assert_valid_path(self, problem, result):
        self.assertEqual(result.path[0], problem.origin)
        self.assertEqual(result.path[-1], result.goal)
        self.assertTrue(problem.is_goal(result.goal))
        self.assertEqual(len(set(result.path)), len(result.path))   # no repeated node
        cost = sum(problem.graph.edge_cost(a, b) for a, b in zip(result.path, result.path[1:]))
        self.assertEqual(cost, result.cost)

    def test_against_reference_answers(self):
        rng = random.Random(30019)
        for trial in range(300):
            problem = self.random_problem(rng)
            optimal_cost = self.cheapest_cost(problem)
            optimal_moves = self.fewest_moves(problem)
            with self.subTest(trial=trial):
                results = {m.__name__: m.search(problem) for m in INFORMED}
                for result in results.values():
                    self.assertEqual(result.found, optimal_cost is not None)
                    if result.found:
                        self.assert_valid_path(problem, result)
                if optimal_cost is not None:
                    self.assertEqual(results[astar.__name__].cost, optimal_cost)
                    self.assertEqual(len(results[cus2.__name__].path) - 1, optimal_moves)
                    self.assertEqual(len(bfs.search(problem).path) - 1, optimal_moves)


if __name__ == "__main__":
    unittest.main()
