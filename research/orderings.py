"""Choosing the best ORDER in which to visit the destinations.

With the pairwise distance table every order has a total cost, so the problem
is a shortest open tour over the destinations (an asymmetric travelling-
salesman path: the robot starts at the origin and need not come back).

Three exact solvers are provided so each can check the others:

    best_order_by_permutations   O(k! * k)        tiny k, trivially correct
    best_order_by_dp             O(2^k * k^2)     Held-Karp bitmask DP
    best_walk_by_state_search    O(|V| * 2^k * d) uniform-cost search over
                                 (node, set of destinations seen); needs no table

Among equally cheap orders the permutation and DP solvers both return the one
whose node numbers are lexicographically smallest.
"""

from __future__ import annotations

import heapq
import itertools
import math
from typing import Dict, List, Tuple

from route_finder.graph import Cost
from route_finder.problem import Problem

from .distances import INFINITY, PairwiseDistances

# Costs are sums of whole numbers or short decimals; this absorbs float noise.
TOLERANCE = 1e-9

Order = Tuple[int, ...]


def best_order_by_permutations(table: PairwiseDistances) -> Tuple[Cost, Order]:
    """Try every visiting order. Returns (total cost, order)."""
    best_cost: Cost = INFINITY
    best_order: Order = ()
    if not table.destinations:
        return 0, best_order
    # permutations() yields lexicographic order, so keeping only strict
    # improvements leaves the lexicographically smallest of the cheapest orders.
    for order in itertools.permutations(table.destinations):
        cost: Cost = 0
        previous = table.origin
        for target in order:
            cost += table.distance(previous, target)
            if cost >= best_cost - TOLERANCE:
                break  # already no better than the best order so far
            previous = target
        else:
            best_cost, best_order = cost, order
    return best_cost, best_order


def best_order_by_dp(table: PairwiseDistances) -> Tuple[Cost, Order]:
    """Held-Karp dynamic programme over subsets of destinations.

    remaining[visited][i] is the cheapest cost to visit every destination not
    in the bitmask `visited`, starting from destination i (which is in it).
    Building it "from the end" lets us rebuild the order forwards and always
    pick the smallest node that keeps the total optimal.
    """
    targets = table.destinations
    count = len(targets)
    if count == 0:
        return 0, ()
    everything = (1 << count) - 1
    between = [[table.distance(a, b) for b in targets] for a in targets]

    remaining = [[INFINITY] * count for _ in range(everything + 1)]
    remaining[everything] = [0] * count
    for visited in range(everything - 1, 0, -1):
        for here in range(count):
            if not visited >> here & 1:
                continue
            remaining[visited][here] = min(
                between[here][nxt] + remaining[visited | 1 << nxt][nxt]
                for nxt in range(count) if not visited >> nxt & 1)

    first_leg = [table.distance(table.origin, targets[i]) + remaining[1 << i][i]
                 for i in range(count)]
    best_cost = min(first_leg)
    if best_cost == INFINITY:
        return INFINITY, ()

    here = next(i for i in range(count) if math.isclose(first_leg[i], best_cost, abs_tol=TOLERANCE))
    order = [targets[here]]
    visited = 1 << here
    while visited != everything:
        needed = remaining[visited][here]
        here = next(i for i in range(count)
                    if not visited >> i & 1 and math.isclose(
                        between[here][i] + remaining[visited | 1 << i][i], needed,
                        abs_tol=TOLERANCE))
        order.append(targets[here])
        visited |= 1 << here
    return best_cost, tuple(order)


def best_walk_by_state_search(problem: Problem) -> Tuple[Cost, List[int], int]:
    """Uniform-cost search where a state is (node, destinations seen so far).

    Returns (total cost, walk, states generated). The walk is complete when
    every destination has been seen. This is independent of the distance
    table, which makes it a good cross-check, but its state space is |V| * 2^k.
    """
    targets = sorted(set(problem.destinations))
    bit_of = {target: 1 << i for i, target in enumerate(targets)}
    everything = (1 << len(targets)) - 1
    start = (problem.origin, bit_of.get(problem.origin, 0))

    best: Dict[Tuple[int, int], Cost] = {start: 0}
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    heap: List[Tuple[Cost, int, int]] = [(0, start[0], start[1])]
    generated = 1
    while heap:
        cost, node, seen = heapq.heappop(heap)
        if cost > best[(node, seen)]:
            continue
        if seen == everything:
            return cost, _rebuild_walk((node, seen), came_from), generated
        for neighbour, step in problem.graph.neighbours(node):
            state = (neighbour, seen | bit_of.get(neighbour, 0))
            if cost + step < best.get(state, INFINITY):
                best[state] = cost + step
                came_from[state] = (node, seen)
                generated += 1
                heapq.heappush(heap, (cost + step, state[0], state[1]))
    return INFINITY, [], generated


def _rebuild_walk(end_state: Tuple[int, int],
                  came_from: Dict[Tuple[int, int], Tuple[int, int]]) -> List[int]:
    """Follow predecessor links back from `end_state` to the start state."""
    walk = [end_state[0]]
    state = end_state
    while state in came_from:
        state = came_from[state]
        walk.append(state[0])
    walk.reverse()
    return walk
