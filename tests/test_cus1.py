"""Unit tests for CUS1 (Iterative Deepening DFS). Owner: Person C.

Run from the repository root:
    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.graphgen import random_problem  # noqa: E402
from route_finder.algorithms import bfs, cus1  # noqa: E402
from route_finder.parser import parse_problem_file  # noqa: E402
from test_core import make_problem  # noqa: E402

SAMPLE = ROOT / "tests" / "cases" / "PathFinder-test.txt"


class Cus1SampleTests(unittest.TestCase):
    def test_sample_file(self):
        result = cus1.search(parse_problem_file(SAMPLE))
        self.assertEqual((result.goal, result.nodes_created, result.path, result.cost),
                         (4, 9, [2, 1, 4], 10))

    def test_node_count_is_cumulative_over_deepening_rounds(self):
        # Rounds 0, 1, 2 create 1, 3 and 5 nodes (root re-created each time).
        problem = make_problem([(1, 2, 1), (2, 3, 1)], origin=1, destinations=[3])
        result = cus1.search(problem)
        self.assertEqual(result.nodes_created, 1 + 2 + 3)


class Cus1BehaviourTests(unittest.TestCase):
    def test_origin_is_destination(self):
        result = cus1.search(make_problem([(1, 2, 1)], origin=1, destinations=[1]))
        self.assertEqual((result.goal, result.nodes_created, result.path), (1, 1, [1]))

    def test_unreachable_goal(self):
        result = cus1.search(make_problem([(1, 2, 1), (3, 4, 1)], origin=1, destinations=[4]))
        self.assertFalse(result.found)

    def test_cycle_does_not_loop_forever(self):
        problem = make_problem([(1, 2, 1), (2, 1, 1)], origin=1, destinations=[3])
        self.assertFalse(cus1.search(problem).found)

    def test_edges_are_one_way(self):
        edges = [(1, 2, 1)]
        self.assertFalse(cus1.search(make_problem(edges, origin=2, destinations=[1])).found)
        self.assertEqual(cus1.search(make_problem(edges, origin=1, destinations=[2])).path, [1, 2])

    def test_lower_node_number_wins_a_tie(self):
        problem = make_problem([(1, 5, 1), (1, 3, 1)], origin=1, destinations=[5, 3])
        self.assertEqual(cus1.search(problem).goal, 3)

    def test_fewest_moves_beats_lowest_cost(self):
        problem = make_problem([(1, 3, 100), (1, 2, 1), (2, 3, 1)], origin=1, destinations=[3])
        self.assertEqual(cus1.search(problem).path, [1, 3])

    def test_dead_end_is_backtracked(self):
        # 1 -> 2 is a dead end; the goal is behind 1 -> 3
        problem = make_problem([(1, 2, 1), (1, 3, 1), (3, 4, 1)], origin=1, destinations=[4])
        self.assertEqual(cus1.search(problem).path, [1, 3, 4])

    def test_siblings_of_the_goal_are_counted(self):
        # Round 0 creates 1 node; round 1 creates the root and both children
        # (3 nodes) and pops the goal only after popping its smaller sibling.
        problem = make_problem([(1, 2, 1), (1, 3, 1), (2, 4, 1)], origin=1, destinations=[3])
        result = cus1.search(problem)
        self.assertEqual((result.goal, result.nodes_created), (3, 1 + 3))


class Cus1AgainstOtherMethodsTests(unittest.TestCase):
    def test_same_number_of_moves_as_bfs_on_random_graphs(self):
        for seed in range(40):
            problem = random_problem(12, destination_count=2, seed=seed)
            self.assertEqual(len(cus1.search(problem).path), len(bfs.search(problem).path),
                             f"seed {seed}")

    def test_returns_a_valid_path_to_a_destination(self):
        for seed in range(20):
            problem = random_problem(10, destination_count=1, seed=seed)
            result = cus1.search(problem)
            self.assertTrue(problem.is_goal(result.goal))
            self.assertEqual(result.path[0], problem.origin)
            self.assertEqual(result.path[-1], result.goal)
            steps = zip(result.path, result.path[1:])
            self.assertEqual(sum(problem.graph.edge_cost(a, b) for a, b in steps), result.cost)


if __name__ == "__main__":
    unittest.main()
