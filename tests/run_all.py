"""Runs every search method on every test case and logs the results. Owner: Person D.

    python tests/run_all.py              print a table and write results/run_all.csv
    python tests/run_all.py --repeat 20  time each run 20 times and report the median

Columns: case, method, goal, nodes created, path cost, runtime in milliseconds
and CHECK, which compares the run with the hand-worked answer in
expected_results.py (PASS / FAIL, or "-" for a file with no recorded answer).
The exit code is 1 if any check fails, so the script can guard a commit.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from expected_results import CASES, METHOD_ORDER, matches  # noqa: E402
from route_finder.algorithms import METHODS  # noqa: E402
from route_finder.engine import SearchResult  # noqa: E402
from route_finder.parser import parse_problem_file  # noqa: E402

CASES_DIR = ROOT / "tests" / "cases"
OUTPUT_CSV = ROOT / "results" / "run_all.csv"
FIELDS = ["case", "method", "goal", "nodes", "cost", "ms", "check"]


def time_search(method: str, problem, repeat: int) -> Tuple[SearchResult, float]:
    """Run one method `repeat` times; return the last result and the median time in ms."""
    timings: List[float] = []
    result: Optional[SearchResult] = None
    for _ in range(repeat):
        started = time.perf_counter()
        result = METHODS[method](problem)
        timings.append((time.perf_counter() - started) * 1000)
    assert result is not None
    return result, statistics.median(timings)


def run_everything(repeat: int) -> List[Dict[str, object]]:
    """Run all methods on all case files and return one row per (case, method)."""
    expected_by_file = {case.file: case.expected for case in CASES}
    rows: List[Dict[str, object]] = []
    for path in sorted(CASES_DIR.glob("*.txt")):
        problem = parse_problem_file(path)
        for method in METHOD_ORDER:
            result, milliseconds = time_search(method, problem, repeat)
            expected = expected_by_file.get(path.name, {}).get(method)
            check = "-" if expected is None else ("PASS" if matches(result, expected) else "FAIL")
            rows.append({"case": path.name, "method": method,
                         "goal": result.goal if result.found else "none",
                         "nodes": result.nodes_created,
                         "cost": "" if result.cost is None else f"{result.cost:g}",
                         "ms": f"{milliseconds:.3f}", "check": check})
    return rows


def print_table(rows: List[Dict[str, object]]) -> None:
    """Print the rows as an aligned text table."""
    widths = {f: max(len(f), *(len(str(r[f])) for r in rows)) for f in FIELDS}
    print("  ".join(f.upper().ljust(widths[f]) for f in FIELDS))
    for row in rows:
        print("  ".join(str(row[f]).ljust(widths[f]) for f in FIELDS))


def write_csv(rows: List[Dict[str, object]]) -> None:
    """Save the rows to results/run_all.csv for the report."""
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: Optional[List[str]] = None) -> int:
    """Run the batch; returns 1 if any hand-worked check fails."""
    parser = argparse.ArgumentParser(description="Run every method on every test case.")
    parser.add_argument("--repeat", type=int, default=1,
                        help="runs per method per case; the median time is reported (default 1)")
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    rows = run_everything(args.repeat)
    print_table(rows)
    write_csv(rows)
    failures = sum(row["check"] == "FAIL" for row in rows)
    passes = sum(row["check"] == "PASS" for row in rows)
    print(f"\n{passes} checks passed, {failures} failed. Saved {OUTPUT_CSV}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
