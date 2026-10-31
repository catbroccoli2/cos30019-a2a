"""Benchmarks that produce the data for the report's Insights and Research sections.

    python -m research.benchmark algorithms   # compare the search methods
    python -m research.benchmark research     # scaling of the visit-all solvers
    python -m research.benchmark              # both

CSV files are written to results/ (git-ignored); a summary table is printed.

* algorithms: every implemented method on random graphs of growing size. Each
  run is a separate `python search.py` process with a timeout, because tree
  search can grow exponentially and must be stoppable. Times therefore include
  roughly 30-60 ms of interpreter start-up; node counts are the reliable metric.
* research: the three exact solvers on one graph as the number of destinations grows.
"""

from __future__ import annotations

import csv
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from route_finder.algorithms import METHODS
from route_finder.parser import parse_problem_file

from .distances import PairwiseDistances
from .graphgen import random_problem, to_problem_text
from .orderings import best_order_by_dp, best_order_by_permutations, best_walk_by_state_search
from .visit_all import DP_LIMIT, visit_all

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

GRAPH_SIZES = (10, 20, 30, 40, 60, 80)
# "random": destination chosen at random; "far": the node most moves from the origin.
SCENARIOS = ("random", "far")
SEEDS = range(10)
RUN_TIMEOUT_SECONDS = 5

RESEARCH_NODE_COUNT = 40
RESEARCH_SEEDS = range(3)
RESEARCH_DESTINATION_COUNTS = range(1, DP_LIMIT + 1)
# Largest k tried per solver, so a whole run finishes in about a minute.
SOLVER_LIMITS = {"perm": 10, "dp": DP_LIMIT, "ucs": 14}

NOT_IMPLEMENTED_EXIT_CODE = 3   # search.py: method stub not written yet


def _run_method(problem_file: Path, method: str) -> Dict[str, object]:
    """Run `search.py` once and return its parsed result (or why it has none)."""
    started = time.perf_counter()
    try:
        done = subprocess.run([sys.executable, str(ROOT / "search.py"), str(problem_file), method],
                              capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "seconds": RUN_TIMEOUT_SECONDS}
    seconds = time.perf_counter() - started
    if done.returncode == NOT_IMPLEMENTED_EXIT_CODE:
        return {"status": "not_implemented", "seconds": seconds}
    lines = done.stdout.splitlines()
    if done.returncode != 0 or len(lines) < 2:
        return {"status": "error", "seconds": seconds}
    if lines[1].startswith("No goal"):
        return {"status": "no_goal", "seconds": seconds,
                "nodes_created": int(lines[1].rsplit(";", 1)[1])}
    goal, nodes = lines[1].split()
    path = [int(n) for n in lines[2].split(" -> ")]
    return {"status": "ok", "seconds": seconds, "goal": int(goal), "nodes_created": int(nodes),
            "moves": len(path) - 1, "path": path}


def benchmark_algorithms() -> List[Dict[str, object]]:
    """Run every method on random graphs; returns one row per (graph, method)."""
    rows: List[Dict[str, object]] = []
    with tempfile.TemporaryDirectory() as folder:
        for scenario in SCENARIOS:
            for size in GRAPH_SIZES:
                for seed in SEEDS:
                    problem = random_problem(size, destination_count=1, seed=seed,
                                             far_destination=scenario == "far")
                    problem_file = Path(folder) / f"{scenario}_n{size}_s{seed}.txt"
                    problem_file.write_text(to_problem_text(problem), encoding="utf-8")
                    graph = parse_problem_file(problem_file).graph
                    for method in METHODS:
                        outcome = _run_method(problem_file, method)
                        path: Optional[List[int]] = outcome.pop("path", None)
                        cost = (sum(graph.edge_cost(a, b) for a, b in zip(path, path[1:]))
                                if path else "")
                        rows.append({"scenario": scenario, "nodes": size, "seed": seed,
                                     "method": method, "status": outcome["status"],
                                     "nodes_created": outcome.get("nodes_created", ""),
                                     "moves": outcome.get("moves", ""), "cost": cost,
                                     "seconds": round(float(outcome["seconds"]), 4)})
    return rows


def _timed(function, *args):
    """Call `function` and return (result, elapsed seconds)."""
    started = time.perf_counter()
    result = function(*args)
    return result, time.perf_counter() - started


def benchmark_research() -> List[Dict[str, object]]:
    """Time the exact solvers as destinations grow; checks they agree on cost."""
    rows: List[Dict[str, object]] = []
    for count in RESEARCH_DESTINATION_COUNTS:
        for seed in RESEARCH_SEEDS:
            problem = random_problem(RESEARCH_NODE_COUNT, destination_count=count, seed=seed)
            table, table_seconds = _timed(PairwiseDistances, problem)
            costs = {}
            row: Dict[str, object] = {"destinations": count, "seed": seed,
                                      "pairwise_dijkstra_s": round(table_seconds, 5)}
            for solver, limit in SOLVER_LIMITS.items():
                if count > limit:
                    row[f"{solver}_s"] = ""
                    continue
                if solver == "ucs":
                    (cost, _, generated), seconds = _timed(best_walk_by_state_search, problem)
                    row["ucs_states"] = generated
                else:
                    solve = best_order_by_permutations if solver == "perm" else best_order_by_dp
                    (cost, _), seconds = _timed(solve, table)
                costs[solver] = cost
                row[f"{solver}_s"] = round(seconds, 5)
            if len(set(costs.values())) != 1:
                raise AssertionError(f"solvers disagree for k={count}, seed={seed}: {costs}")
            row["optimal_cost"] = next(iter(costs.values()))
            row["walk_nodes"] = len(visit_all(problem, "dp").walk)
            rows.append(row)
    return rows


def _write_csv(name: str, rows: List[Dict[str, object]]) -> Path:
    """Write rows to results/<name>; the header is the union of all row keys."""
    RESULTS.mkdir(exist_ok=True)
    fields: List[str] = []
    for row in rows:
        fields.extend(key for key in row if key not in fields)
    path = RESULTS / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, restval="")
        writer.writeheader()
        writer.writerows(rows)
    return path


def _median(values: List[float]) -> str:
    return f"{statistics.median(values):.0f}" if values else "-"


def _print_algorithm_summary(rows: List[Dict[str, object]]) -> None:
    methods = [m for m in METHODS if any(r["method"] == m and r["status"] != "not_implemented"
                                         for r in rows)]
    for scenario in SCENARIOS:
        print(f"\nScenario '{scenario}': median nodes created over finished runs "
              "(brackets: timeouts/runs)")
        print("graph nodes | " + " | ".join(f"{m:>18}" for m in methods))
        for size in GRAPH_SIZES:
            cells = []
            for method in methods:
                runs = [r for r in rows if r["scenario"] == scenario
                        and r["nodes"] == size and r["method"] == method]
                done = [r["nodes_created"] for r in runs if r["status"] in ("ok", "no_goal")]
                timeouts = sum(r["status"] == "timeout" for r in runs)
                cells.append(f"{_median(done):>8} ({timeouts}/{len(runs)})".rjust(18))
            print(f"{size:>11} | " + " | ".join(cells))


def _print_research_summary(rows: List[Dict[str, object]]) -> None:
    print("\nMedian seconds per solver (blank = not run at that size)")
    print("k  | pairwise |     perm |       dp |      ucs | ucs states")
    for count in RESEARCH_DESTINATION_COUNTS:
        group = [r for r in rows if r["destinations"] == count]

        def med(key: str) -> str:
            values = [float(r[key]) for r in group if r.get(key, "") != ""]
            return f"{statistics.median(values):.4f}" if values else ""

        states = [r["ucs_states"] for r in group if r.get("ucs_states", "") != ""]
        print(f"{count:<2} | {med('pairwise_dijkstra_s'):>8} | {med('perm_s'):>8} | "
              f"{med('dp_s'):>8} | {med('ucs_s'):>8} | {_median(states):>10}")


def main(argv: Optional[List[str]] = None) -> int:
    """Run the requested benchmarks and write their CSV files."""
    args = sys.argv[1:] if argv is None else argv
    which = args[0] if args else "all"
    if which not in ("all", "algorithms", "research"):
        print("Usage: python -m research.benchmark [algorithms | research | all]", file=sys.stderr)
        return 2
    if which in ("all", "algorithms"):
        rows = benchmark_algorithms()
        print(f"wrote {_write_csv('algorithms.csv', rows)}")
        _print_algorithm_summary(rows)
    if which in ("all", "research"):
        rows = benchmark_research()
        print(f"wrote {_write_csv('research_scaling.csv', rows)}")
        _print_research_summary(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
