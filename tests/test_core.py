"""Unit tests for Person A's code: parser, graph, frontiers, DFS and BFS, CLI.

Run from the repository root:
    python -m unittest discover -s tests -v
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from route_finder.algorithms import bfs, dfs  # noqa: E402
from route_finder.frontier import PriorityFrontier, QueueFrontier, StackFrontier  # noqa: E402
from route_finder.output import format_result  # noqa: E402
from route_finder.parser import ParseError, parse_problem_file, parse_problem_text  # noqa: E402
from route_finder.search_node import SearchNode  # noqa: E402

SAMPLE = ROOT / "tests" / "cases" / "PathFinder-test.txt"


def make_problem(edges, origin, destinations, node_count=None):
    """Build a Problem from edge triples; nodes are laid out on a line."""
    ids = {origin, *destinations}
    for a, b, _ in edges:
        ids.update((a, b))
    if node_count:
        ids.update(range(1, node_count + 1))
    lines = ["Nodes:"] + [f"{i}: ({i},0)" for i in sorted(ids)]
    lines += ["Edges:"] + [f"({a},{b}): {c}" for a, b, c in edges]
    lines += ["Origin:", str(origin), "Destinations:", "; ".join(map(str, destinations))]
    return parse_problem_text("\n".join(lines))


class ParserTests(unittest.TestCase):
    def test_sample_file(self):
        problem = parse_problem_file(SAMPLE)
        self.assertEqual(len(problem.graph), 6)
        self.assertEqual(problem.origin, 2)
        self.assertEqual(problem.destinations, (5, 4))
        self.assertEqual(problem.graph.coordinates(5), (5, 6))
        self.assertEqual(problem.graph.edge_cost(1, 3), 5)

    def test_edges_are_directed(self):
        graph = parse_problem_file(SAMPLE).graph
        self.assertEqual([n for n, _ in graph.neighbours(2)], [1, 3])
        self.assertEqual([n for n, _ in graph.neighbours(1)], [3, 4])  # no 1 -> 2
        self.assertEqual([n for n, _ in graph.neighbours(6)], [3])

    def test_neighbours_sorted_even_if_file_is_not(self):
        problem = parse_problem_text(
            "Nodes:\n1: (0,0)\n2: (1,0)\n3: (2,0)\nEdges:\n(1,3): 1\n(1,2): 1\n"
            "Origin:\n1\nDestinations:\n3\n")
        self.assertEqual([n for n, _ in problem.graph.neighbours(1)], [2, 3])

    def test_windows_line_endings_bom_and_spacing(self):
        text = "﻿Nodes:\r\n1: (0,0)\r\n  2 :  ( 3 , 4 ) \r\nEdges:\r\n( 1 , 2 ) : 5\r\n\r\n" \
               "Origin:\r\n1\r\nDestinations:\r\n2;\r\n"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.txt"
            path.write_bytes(text.encode("utf-8"))
            problem = parse_problem_file(path)
        self.assertEqual(problem.destinations, (2,))
        self.assertEqual(problem.graph.coordinates(2), (3, 4))

    def test_decimal_values_and_inline_headers(self):
        problem = parse_problem_text(
            "nodes:\n1: (0.5,1.5)\n2: (3,4)\nedges:\n(1,2): 2.5\nOrigin: 1\nDestinations: 2\n")
        self.assertEqual(problem.graph.edge_cost(1, 2), 2.5)
        self.assertEqual(problem.graph.coordinates(1), (0.5, 1.5))

    def test_multiple_destinations_and_duplicates(self):
        problem = parse_problem_text(
            "Nodes:\n1: (0,0)\n2: (1,0)\n3: (2,0)\nEdges:\nOrigin:\n1\n"
            "Destinations:\n2; 3; 2\n")
        self.assertEqual(problem.destinations, (2, 3))

    def test_errors(self):
        good = "Nodes:\n1: (0,0)\n2: (1,0)\nEdges:\n(1,2): 1\nOrigin:\n1\nDestinations:\n2\n"
        parse_problem_text(good)  # sanity: the template itself is valid
        bad_cases = {
            "empty file": "",
            "missing Destinations": good.split("Destinations:")[0],
            "empty Nodes": "Nodes:\nEdges:\nOrigin:\n1\nDestinations:\n2\n",
            "empty Destinations": good.replace("Destinations:\n2\n", "Destinations:\n"),
            "bad node line": good.replace("1: (0,0)", "1 (0,0)"),
            "bad edge line": good.replace("(1,2): 1", "1->2: 1"),
            "edge to undefined node": good.replace("(1,2): 1", "(1,9): 1"),
            "origin undefined": good.replace("Origin:\n1", "Origin:\n7"),
            "destination undefined": good.replace("Destinations:\n2", "Destinations:\n8"),
            "two origins": good.replace("Origin:\n1", "Origin:\n1\n2"),
            "duplicate node id": good.replace("2: (1,0)", "1: (1,0)"),
            "text before header": "hello\n" + good,
            "repeated section": good + "Origin:\n1\n",
        }
        for name, text in bad_cases.items():
            with self.subTest(name):
                with self.assertRaises(ParseError):
                    parse_problem_text(text)


class FrontierTests(unittest.TestCase):
    @staticmethod
    def node(state, order, g=0):
        return SearchNode(state, None, g, 0, order)

    def test_priority_ties_use_node_number_then_insertion_order(self):
        frontier = PriorityFrontier(lambda n: 10)
        frontier.push(self.node(7, order=0))
        frontier.push(self.node(4, order=1))
        frontier.push(self.node(4, order=2))   # same node number, added later
        frontier.push(self.node(9, order=3))
        popped = [(frontier.pop().state, ) for _ in range(4)]
        self.assertEqual(popped, [(4,), (4,), (7,), (9,)])

    def test_priority_value_beats_node_number(self):
        frontier = PriorityFrontier(lambda n: {1: 5, 2: 3}[n.state])
        frontier.push(self.node(1, 0))
        frontier.push(self.node(2, 1))
        self.assertEqual(frontier.pop().state, 2)

    def test_priority_float_noise_is_a_tie(self):
        values = {3: 10.000000000000002, 8: 10.0}
        frontier = PriorityFrontier(lambda n: values[n.state])
        frontier.push(self.node(8, 0))
        frontier.push(self.node(3, 1))
        self.assertEqual(frontier.pop().state, 3)   # tie -> lower node number

    def test_stack_pops_lowest_child_first_and_is_lifo(self):
        frontier = StackFrontier()
        frontier.extend([self.node(1, 0), self.node(2, 1), self.node(3, 2)])
        self.assertEqual(frontier.pop().state, 1)
        frontier.extend([self.node(8, 3), self.node(9, 4)])
        self.assertEqual([frontier.pop().state for _ in range(3)], [8, 9, 2])

    def test_queue_is_fifo(self):
        frontier = QueueFrontier()
        frontier.extend([self.node(5, 0), self.node(2, 1)])
        self.assertEqual([frontier.pop().state, frontier.pop().state], [5, 2])


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.sample = parse_problem_file(SAMPLE)

    def test_bfs_on_sample(self):
        result = bfs.search(self.sample)
        self.assertEqual((result.goal, result.nodes_created, result.path), (4, 10, [2, 1, 4]))
        self.assertEqual(result.cost, 10)

    def test_dfs_on_sample(self):
        result = dfs.search(self.sample)
        self.assertEqual((result.goal, result.nodes_created, result.path), (5, 7, [2, 1, 3, 5]))

    def test_origin_is_destination(self):
        problem = make_problem([(1, 2, 3)], origin=1, destinations=[1])
        for search in (bfs.search, dfs.search):
            result = search(problem)
            self.assertEqual((result.goal, result.nodes_created, result.path), (1, 1, [1]))

    def test_unreachable_destination(self):
        problem = make_problem([(1, 2, 1)], origin=1, destinations=[3])
        for search in (bfs.search, dfs.search):
            result = search(problem)
            self.assertFalse(result.found)
            self.assertEqual(result.nodes_created, 2)

    def test_one_way_edge_blocks_reverse_travel(self):
        problem = make_problem([(1, 2, 1)], origin=2, destinations=[1])
        self.assertFalse(bfs.search(problem).found)

    def test_cycle_terminates(self):
        problem = make_problem([(1, 2, 1), (2, 1, 1), (2, 3, 1), (3, 2, 1)],
                               origin=1, destinations=[4])
        for search in (bfs.search, dfs.search):
            self.assertFalse(search(problem).found)

    def test_dfs_takes_lowest_numbered_branch_first(self):
        # 1 -> 2 -> 4 and 1 -> 3 -> 4: DFS must go via 2 (smaller) first.
        problem = make_problem([(1, 2, 9), (1, 3, 1), (2, 4, 9), (3, 4, 1)],
                               origin=1, destinations=[4])
        self.assertEqual(dfs.search(problem).path, [1, 2, 4])

    def test_bfs_finds_fewest_moves_not_lowest_cost(self):
        # Direct edge costs 100 but is one move; the long way costs 3 but is 3 moves.
        problem = make_problem([(1, 4, 100), (1, 2, 1), (2, 3, 1), (3, 4, 1)],
                               origin=1, destinations=[4])
        result = bfs.search(problem)
        self.assertEqual(result.path, [1, 4])
        self.assertEqual(result.cost, 100)

    def test_bfs_same_depth_goals_prefers_first_generated(self):
        # Goals 2 and 3 are both one move away; 2 is generated first.
        problem = make_problem([(1, 3, 1), (1, 2, 1)], origin=1, destinations=[2, 3])
        self.assertEqual(bfs.search(problem).goal, 2)


class OutputAndCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "search.py"), *args],
                              capture_output=True, text=True, cwd=str(ROOT))

    def test_cli_output_format_bfs(self):
        done = self.run_cli("tests/cases/PathFinder-test.txt", "BFS")
        self.assertEqual(done.returncode, 0)
        self.assertEqual(done.stdout.splitlines(),
                         ["tests/cases/PathFinder-test.txt BFS", "4 10", "2 -> 1 -> 4"])

    def test_cli_method_is_case_insensitive(self):
        done = self.run_cli("tests/cases/PathFinder-test.txt", "dfs")
        self.assertEqual(done.stdout.splitlines()[0], "tests/cases/PathFinder-test.txt DFS")

    def test_cli_bad_arguments(self):
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(self.run_cli("tests/cases/PathFinder-test.txt").returncode, 2)
        self.assertEqual(self.run_cli("tests/cases/PathFinder-test.txt", "XYZ").returncode, 2)

    def test_cli_missing_and_malformed_file(self):
        self.assertEqual(self.run_cli("no_such_file.txt", "BFS").returncode, 1)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.txt"
            path.write_text("garbage", encoding="utf-8")
            self.assertEqual(self.run_cli(str(path), "BFS").returncode, 1)

    def test_no_path_format(self):
        problem = make_problem([(1, 2, 1)], origin=1, destinations=[3])
        text = format_result("f.txt", "BFS", bfs.search(problem))
        self.assertEqual(text.splitlines(), ["f.txt BFS", "No goal is reachable; 2"])


if __name__ == "__main__":
    unittest.main()
