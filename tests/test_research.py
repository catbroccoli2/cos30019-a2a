"""Unit tests for the research feature (visit ALL destinations). Owner: Person C.

Run from the repository root:
    python -m unittest discover -s tests -v
"""

import itertools
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.distances import INFINITY, shortest_paths_from  # noqa: E402
from research.graphgen import random_problem, to_problem_text  # noqa: E402
from research.visit_all import DP_LIMIT, SOLVERS, visit_all  # noqa: E402
from route_finder.parser import parse_problem_file, parse_problem_text  # noqa: E402
from test_core import make_problem  # noqa: E402

SAMPLE = ROOT / "tests" / "cases" / "PathFinder-test.txt"
EXACT_SOLVERS = ("perm", "dp", "ucs")


def walk_cost(problem, walk):
    """Total cost of a walk; raises KeyError if it uses a missing edge."""
    return sum(problem.graph.edge_cost(a, b) for a, b in zip(walk, walk[1:]))


class SampleTests(unittest.TestCase):
    def test_sample_file_every_solver(self):
        problem = parse_problem_file(SAMPLE)
        for solver in SOLVERS:
            result = visit_all(problem, solver)
            self.assertEqual((result.cost, result.walk, result.visit_order),
                             (17, [2, 1, 4, 5], [4, 5]), solver)


class EdgeCaseTests(unittest.TestCase):
    def test_one_way_costs_decide_the_order(self):
        # 1->2 and 2->3 are cheap but 3->2 is expensive, so visit 2 before 3.
        problem = make_problem([(1, 2, 1), (2, 3, 1), (3, 2, 50), (3, 1, 1), (2, 1, 50)],
                               origin=1, destinations=[3, 2])
        self.assertEqual(visit_all(problem).visit_order, [2, 3])

    def test_destination_on_the_way_costs_nothing_extra(self):
        problem = make_problem([(1, 2, 5), (2, 3, 5), (3, 4, 5)], origin=1, destinations=[4, 2])
        result = visit_all(problem)
        self.assertEqual((result.cost, result.visit_order, result.walk),
                         (15, [2, 4], [1, 2, 3, 4]))

    def test_origin_listed_as_destination_is_free(self):
        problem = make_problem([(1, 2, 4), (2, 1, 4)], origin=1, destinations=[1, 2])
        self.assertEqual(visit_all(problem).cost, 4)

    def test_only_the_origin_to_visit(self):
        result = visit_all(make_problem([(1, 2, 4)], origin=1, destinations=[1]))
        self.assertEqual((result.reachable, result.cost, result.walk), (True, 0, [1]))

    def test_single_destination_is_a_shortest_path(self):
        problem = make_problem([(1, 2, 1), (2, 3, 1), (1, 3, 5)], origin=1, destinations=[3])
        self.assertEqual(visit_all(problem).walk, [1, 2, 3])

    def test_destination_unreachable_from_the_origin(self):
        problem = make_problem([(1, 2, 1), (3, 1, 1)], origin=1, destinations=[2, 3])
        for solver in EXACT_SOLVERS:
            result = visit_all(problem, solver)
            self.assertFalse(result.reachable, solver)
        self.assertEqual(visit_all(problem, "perm").unreachable, [3])

    def test_destinations_that_cannot_reach_each_other(self):
        problem = make_problem([(1, 2, 1), (1, 3, 1)], origin=1, destinations=[2, 3])
        for solver in EXACT_SOLVERS:
            self.assertFalse(visit_all(problem, solver).reachable, solver)

    def test_unknown_solver_and_too_many_destinations(self):
        problem = make_problem([(1, 2, 1)], origin=1, destinations=[2])
        with self.assertRaises(ValueError):
            visit_all(problem, "magic")
        big = random_problem(DP_LIMIT + 3, destination_count=DP_LIMIT + 1, seed=1)
        with self.assertRaises(ValueError):
            visit_all(big, "dp")

    def test_dijkstra_respects_edge_direction(self):
        problem = make_problem([(1, 2, 3)], origin=1, destinations=[2])
        self.assertEqual(shortest_paths_from(problem, 1)[0], {1: 0, 2: 3})
        self.assertEqual(shortest_paths_from(problem, 2)[0], {2: 0})
        self.assertEqual(INFINITY, float("inf"))


class SolverAgreementTests(unittest.TestCase):
    def test_all_exact_solvers_find_the_same_cost(self):
        for seed in range(40):
            for count in (1, 2, 3, 5):
                problem = random_problem(18, destination_count=count, seed=seed)
                results = {s: visit_all(problem, s) for s in EXACT_SOLVERS}
                costs = {s: r.cost for s, r in results.items()}
                self.assertEqual(len(set(costs.values())), 1, (seed, count, costs))

    def test_permutations_and_dp_pick_the_same_order(self):
        for seed in range(40):
            problem = random_problem(18, destination_count=5, seed=seed)
            self.assertEqual(visit_all(problem, "perm").walk, visit_all(problem, "dp").walk)

    def test_walk_is_valid_and_costs_what_is_claimed(self):
        for seed in range(20):
            problem = random_problem(20, destination_count=4, seed=seed)
            result = visit_all(problem)
            self.assertEqual(walk_cost(problem, result.walk), result.cost)
            self.assertEqual(result.walk[0], problem.origin)
            self.assertTrue(set(problem.destinations) <= set(result.walk))
            self.assertEqual(sorted(result.visit_order), sorted(set(problem.destinations)))

    def test_matches_an_independent_floyd_warshall_oracle(self):
        problem = random_problem(9, destination_count=4, seed=7)
        nodes = problem.graph.node_ids()
        dist = {a: {b: 0 if a == b else INFINITY for b in nodes} for a in nodes}
        for a in nodes:
            for b, cost in problem.graph.neighbours(a):
                dist[a][b] = min(dist[a][b], cost)
        for via, a, b in itertools.product(nodes, nodes, nodes):
            dist[a][b] = min(dist[a][b], dist[a][via] + dist[via][b])
        best = min(sum(dist[x][y] for x, y in zip((problem.origin,) + order, order))
                   for order in itertools.permutations(problem.destinations))
        self.assertEqual(visit_all(problem).cost, best)


class GeneratorTests(unittest.TestCase):
    def test_same_seed_same_problem(self):
        self.assertEqual(to_problem_text(random_problem(15, 3, seed=4)),
                         to_problem_text(random_problem(15, 3, seed=4)))

    def test_round_trips_through_the_parser(self):
        problem = random_problem(15, destination_count=3, seed=4)
        again = parse_problem_text(to_problem_text(problem))
        self.assertEqual(again.destinations, tuple(problem.destinations))
        self.assertEqual(again.origin, problem.origin)
        self.assertEqual(to_problem_text(again), to_problem_text(problem))

    def test_edge_costs_never_below_straight_line_distance(self):
        problem = random_problem(25, seed=3)
        graph = problem.graph
        for a in graph.node_ids():
            for b, cost in graph.neighbours(a):
                (x1, y1), (x2, y2) = graph.coordinates(a), graph.coordinates(b)
                self.assertGreaterEqual(cost, ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 - 1e-9)

    def test_far_destination_needs_the_most_moves(self):
        problem = random_problem(25, seed=3, far_destination=True)
        (far,) = problem.destinations
        moves = {}
        frontier = [problem.origin]
        moves[problem.origin] = 0
        for node in frontier:  # breadth-first walk, appending as it goes
            for neighbour, _ in problem.graph.neighbours(node):
                if neighbour not in moves:
                    moves[neighbour] = moves[node] + 1
                    frontier.append(neighbour)
        self.assertEqual(moves[far], max(moves.values()))

    def test_every_node_reaches_every_other(self):
        problem = random_problem(25, seed=3)
        for node in problem.graph.node_ids():
            self.assertEqual(len(shortest_paths_from(problem, node)[0]), 25)


if __name__ == "__main__":
    unittest.main()
