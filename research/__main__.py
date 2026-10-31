"""Command line for the research feature.

    python -m research <problem file> [auto|perm|dp|ucs]

Output (a deliberate extension of the assignment's format, which has a single goal):
    filename RESEARCH
    visit_order <destinations in first-reached order>  total_cost <cost>
    walk from origin through every destination
"""

from __future__ import annotations

import sys
from typing import List, Optional

from route_finder.output import PATH_SEPARATOR
from route_finder.parser import ParseError, parse_problem_file

from .visit_all import SOLVERS, visit_all

USAGE = f"Usage: python -m research <filename> [{' | '.join(SOLVERS)}]"


def main(argv: Optional[List[str]] = None) -> int:
    """Run the research feature; returns a process exit code."""
    args = sys.argv[1:] if argv is None else argv
    if not 1 <= len(args) <= 2 or (len(args) == 2 and args[1] not in SOLVERS):
        print(USAGE, file=sys.stderr)
        return 2
    try:
        problem = parse_problem_file(args[0])
    except OSError as exc:
        print(f"Error: cannot read '{args[0]}': {exc.strerror}", file=sys.stderr)
        return 1
    except ParseError as exc:
        print(f"Error: invalid problem file '{args[0]}': {exc}", file=sys.stderr)
        return 1

    try:
        result = visit_all(problem, args[1] if len(args) == 2 else "auto")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"{args[0]} RESEARCH ({result.solver})")
    if not result.reachable:
        reason = f"; not reachable from the origin: {result.unreachable}" if result.unreachable else ""
        print(f"No walk visits every destination{reason}")
    else:
        print(f"visit_order {' '.join(map(str, result.visit_order))}  total_cost {result.cost:g}")
        print(PATH_SEPARATOR.join(map(str, result.walk)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
