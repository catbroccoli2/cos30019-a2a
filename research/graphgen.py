"""Random Route Finding problems for tests and benchmarks.

Every generated problem is:
  * strongly connected - a random spanning tree is added in BOTH directions,
    so every destination can be reached from the origin and from every other
    destination, and the research feature always has an answer;
  * admissible for the straight-line heuristic - each edge costs at least the
    straight-line distance between its ends (cost = ceil(length * 1.0..1.5));
  * partly one-way - some extra edges have no reverse edge, like the arrows in
    the assignment's figure.
The same seed always gives the same problem.
"""

from __future__ import annotations

import math
import random
from collections import deque
from typing import Dict, List, Tuple

from route_finder.graph import Graph
from route_finder.problem import Problem

NEAREST_NEIGHBOURS = 2   # each node may get extra edges to this many closest nodes


def _distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def farthest_node(graph: Graph, origin: int) -> int:
    """The node needing the most moves from `origin` (lowest number wins ties)."""
    moves = {origin: 0}
    queue = deque([origin])
    while queue:
        node = queue.popleft()
        for neighbour, _ in graph.neighbours(node):
            if neighbour not in moves:
                moves[neighbour] = moves[node] + 1
                queue.append(neighbour)
    return min(moves, key=lambda n: (-moves[n], n))


def random_problem(node_count: int, destination_count: int = 1, seed: int = 0,
                   extra_edge_chance: float = 0.5, one_way_chance: float = 0.3,
                   far_destination: bool = False) -> Problem:
    """Build a random strongly connected problem with the given size.

    With `far_destination` the single destination is the node farthest from
    the origin in moves, which forces the search methods to work hard.
    """
    rng = random.Random(seed)
    side = max(12, math.ceil(math.sqrt(node_count) * 4))     # keeps the grid roomy
    spots = rng.sample([(x, y) for x in range(1, side + 1) for y in range(1, side + 1)],
                       node_count)
    position = {i + 1: spot for i, spot in enumerate(spots)}

    def edge_cost(a: int, b: int) -> int:
        return max(1, math.ceil(_distance(position[a], position[b]) * rng.uniform(1.0, 1.5)))

    edges: Dict[Tuple[int, int], int] = {}
    order = list(position)
    rng.shuffle(order)
    for index in range(1, node_count):
        new = order[index]
        # Attach to the nearest of a few earlier nodes: short, map-like edges.
        candidates = rng.sample(order[:index], min(3, index))
        old = min(candidates, key=lambda c: _distance(position[new], position[c]))
        edges[(new, old)] = edge_cost(new, old)
        edges[(old, new)] = edge_cost(old, new)

    for node in position:
        closest = sorted((o for o in position if o != node),
                         key=lambda o: _distance(position[node], position[o]))
        for other in closest[:NEAREST_NEIGHBOURS]:
            if (node, other) in edges or rng.random() > extra_edge_chance:
                continue
            edges[(node, other)] = edge_cost(node, other)
            if rng.random() > one_way_chance and (other, node) not in edges:
                edges[(other, node)] = edge_cost(other, node)

    graph = Graph()
    for node, (x, y) in position.items():
        graph.add_node(node, x, y)
    for (source, target), cost in sorted(edges.items()):
        graph.add_edge(source, target, cost)
    origin = rng.choice(list(position))
    if far_destination:
        return Problem(graph, origin, [farthest_node(graph, origin)])
    others = [n for n in position if n != origin]
    destinations = rng.sample(others, min(destination_count, len(others)))
    return Problem(graph, origin, destinations)


def to_problem_text(problem: Problem) -> str:
    """Render a problem in the assignment's file format."""
    graph = problem.graph
    lines: List[str] = ["Nodes:"]
    for node in graph.node_ids():
        x, y = graph.coordinates(node)
        lines.append(f"{node}: ({x},{y})")
    lines.append("Edges:")
    for node in graph.node_ids():
        lines.extend(f"({node},{target}): {cost}" for target, cost in graph.neighbours(node))
    lines += ["Origin:", str(problem.origin),
              "Destinations:", "; ".join(map(str, problem.destinations)), ""]
    return "\n".join(lines)
