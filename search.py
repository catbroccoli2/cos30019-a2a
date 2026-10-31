"""Command-line entry point.

Usage:
    python search.py <filename> <method>

where <method> is one of DFS, BFS, GBFS, AS, CUS1, CUS2.

On success it prints:
    filename method
    goal number_of_nodes
    path
"""

from __future__ import annotations

import sys
from typing import List, Optional

from route_finder.algorithms import METHODS
from route_finder.output import format_result
from route_finder.parser import ParseError, parse_problem_file

USAGE = ("Usage: python search.py <filename> <method>\n"
         "  method: " + " | ".join(METHODS))

# Exit codes: 0 success, 1 bad input file, 2 bad command line, 3 method missing.


def main(argv: Optional[List[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if len(args) != 2:
        print(USAGE, file=sys.stderr)
        return 2

    filename, method = args[0], args[1].upper()
    if method not in METHODS:
        print(f"Error: unknown method '{args[1]}'.\n{USAGE}", file=sys.stderr)
        return 2

    try:
        problem = parse_problem_file(filename)
    except OSError as exc:
        print(f"Error: cannot read '{filename}': {exc.strerror}", file=sys.stderr)
        return 1
    except ParseError as exc:
        print(f"Error: invalid problem file '{filename}': {exc}", file=sys.stderr)
        return 1

    try:
        result = METHODS[method](problem)
    except NotImplementedError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3

    print(format_result(filename, method, result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
