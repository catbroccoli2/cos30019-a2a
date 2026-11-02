"""Peak frontier size of every method on the benchmark graphs (the report's memory measure).

    python -m research.frontier_peak

The frontier is the set of nodes that have been generated but not yet expanded, so its
largest size is a simple, machine-independent measure of how much a method must keep in
memory. It is measured by wrapping the shared frontier classes while a search runs, so no
search method needs to change. Iterative deepening (CUS1) and IDA* (CUS2) build a new
frontier in every round; their peak is the largest over all rounds.

The graphs are the same 80-node graphs (seeds 0 to 9, both scenarios) as the benchmark in
`research.benchmark`. A run that creates more than NODE_CAP nodes is counted as not finished.
"""

from __future__ import annotations

import contextlib
import statistics
from typing import Dict, Iterator, List, Optional

from route_finder import frontier as frontier_module
from route_finder.algorithms import METHODS
from route_finder.engine import SearchSpace
from route_finder.problem import Problem

from .graphgen import random_problem

GRAPH_SIZE = 80
SEEDS = range(10)
SCENARIOS = ("random", "far")
NODE_CAP = 1_000_000   # about where the benchmark's 5-second limit is reached


class NodeCapExceeded(Exception):
    """Raised when one search creates more than NODE_CAP nodes."""


class _Meter:
    """Largest frontier length and number of nodes seen during one search."""

    def __init__(self) -> None:
        self.peak = 0
        self.nodes = 0


@contextlib.contextmanager
def _instrumented(meter: _Meter) -> Iterator[None]:
    """Wrap the frontier classes and node creation so `meter` records one search."""
    classes = (frontier_module.StackFrontier, frontier_module.QueueFrontier,
               frontier_module.PriorityFrontier)
    saved = []
    for cls in classes:
        for name in ("push", "extend"):
            original = getattr(cls, name)
            saved.append((cls, name, cls.__dict__.get(name)))

            def wrapper(self, *args, _original=original, **kwargs):
                result = _original(self, *args, **kwargs)
                meter.peak = max(meter.peak, len(self))
                return result
            setattr(cls, name, wrapper)

    original_new_node = SearchSpace._new_node

    def counting_new_node(self, *args, **kwargs):
        meter.nodes += 1
        if meter.nodes > NODE_CAP:
            raise NodeCapExceeded
        return original_new_node(self, *args, **kwargs)
    SearchSpace._new_node = counting_new_node
    try:
        yield
    finally:
        SearchSpace._new_node = original_new_node
        for cls, name, original in saved:
            if original is None:
                delattr(cls, name)
            else:
                setattr(cls, name, original)


def peak_frontier(method: str, problem: Problem) -> Optional[int]:
    """Largest frontier size reached by `method` on `problem`, or None if it hit NODE_CAP."""
    meter = _Meter()
    with _instrumented(meter):
        try:
            METHODS[method](problem)
        except NodeCapExceeded:
            return None
    return meter.peak


def measure() -> Dict[str, Dict[str, List[int]]]:
    """Peak frontier sizes by scenario and method over the benchmark graphs."""
    peaks: Dict[str, Dict[str, List[int]]] = {s: {m: [] for m in METHODS} for s in SCENARIOS}
    for scenario in SCENARIOS:
        for seed in SEEDS:
            problem = random_problem(GRAPH_SIZE, destination_count=1, seed=seed,
                                     far_destination=scenario == "far")
            for method in METHODS:
                peak = peak_frontier(method, problem)
                if peak is not None:
                    peaks[scenario][method].append(peak)
    return peaks


def main() -> int:
    """Print the mean and maximum peak frontier size of each method."""
    peaks = measure()
    print(f"Peak frontier size on {GRAPH_SIZE}-node graphs, {len(SEEDS)} graphs per scenario")
    print(f"{'method':<7}" + "".join(f"{s + ' mean (max)':>22}{'finished':>10}" for s in SCENARIOS))
    for method in METHODS:
        cells = ""
        for scenario in SCENARIOS:
            values = peaks[scenario][method]
            cells += f"{statistics.mean(values):>14.1f} ({max(values)}){'':<2}{len(values):>8}/{len(SEEDS)}"
        print(f"{method:<7}{cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
