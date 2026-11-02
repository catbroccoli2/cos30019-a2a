"""Checks every method against the hand-worked results for every file in tests/cases/.

Owner: Omar. Run from the repository root:
    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from expected_results import CASES, METHOD_ORDER, matches  # noqa: E402
from route_finder.algorithms import METHODS  # noqa: E402
from route_finder.parser import parse_problem_file  # noqa: E402

CASES_DIR = ROOT / "tests" / "cases"
MINIMUM_CASES = 15  # the marking scheme requires at least this many


class HandWorkedResultTests(unittest.TestCase):
    def test_every_method_on_every_case(self):
        for case in CASES:
            problem = parse_problem_file(CASES_DIR / case.file)
            for method, expected in case.expected.items():
                with self.subTest(case=case.file, method=method):
                    result = METHODS[method](problem)
                    self.assertTrue(
                        matches(result, expected),
                        f"{case.file} {method}: expected {tuple(expected)}, got "
                        f"{(result.goal, result.nodes_created, result.path, result.cost)}")


class CaseSetTests(unittest.TestCase):
    def test_enough_cases(self):
        self.assertGreaterEqual(len(CASES), MINIMUM_CASES)

    def test_every_case_file_has_expectations_and_vice_versa(self):
        on_disk = {path.name for path in CASES_DIR.glob("*.txt")}
        self.assertEqual(on_disk, {case.file for case in CASES})

    def test_every_case_covers_all_six_methods(self):
        for case in CASES:
            self.assertEqual(set(case.expected), set(METHOD_ORDER), case.file)

    def test_goals_are_destinations_and_paths_start_at_the_origin(self):
        for case in CASES:
            problem = parse_problem_file(CASES_DIR / case.file)
            for method, expected in case.expected.items():
                if expected.goal is None:
                    continue
                with self.subTest(case=case.file, method=method):
                    self.assertTrue(problem.is_goal(expected.goal))
                    self.assertEqual(expected.path[0], problem.origin)
                    self.assertEqual(expected.path[-1], expected.goal)


if __name__ == "__main__":
    unittest.main()
