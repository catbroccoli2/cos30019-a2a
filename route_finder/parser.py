"""Parser for the assignment's problem-file format.

Example file::

    Nodes:
    1: (4,1)
    2: (2,2)
    Edges:
    (2,1): 4
    Origin:
    2
    Destinations:
    1; 3

Section headers are case-insensitive. A value may also follow its header on
the same line (``Origin: 2``). Blank lines and Windows line endings are fine.
Any other problem raises ParseError with the offending line number.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple, Union

from .graph import Graph
from .problem import Problem


class ParseError(ValueError):
    """Raised when a problem file is malformed."""


_NUMBER = r"-?\d+(?:\.\d+)?"
_HEADER_RE = re.compile(r"^(nodes|edges|origin|destinations)\s*:\s*(.*)$", re.IGNORECASE)
_NODE_RE = re.compile(rf"^(\d+)\s*:\s*\(\s*({_NUMBER})\s*,\s*({_NUMBER})\s*\)$")
_EDGE_RE = re.compile(r"^\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*:\s*(\d+(?:\.\d+)?)$")
_INTEGER_RE = re.compile(r"^\d+$")

_SECTIONS = ("nodes", "edges", "origin", "destinations")


def _to_number(text: str) -> Union[int, float]:
    """'4' -> 4 and '4.5' -> 4.5, so whole-number costs stay integers."""
    return float(text) if "." in text else int(text)


def _split_sections(text: str) -> Dict[str, List[Tuple[int, str]]]:
    """Group the non-blank lines of the file by section.

    Returns {section_name: [(line_number, stripped_line), ...]}.
    """
    sections: Dict[str, List[Tuple[int, str]]] = {name: [] for name in _SECTIONS}
    seen = set()
    current = None

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue

        header = _HEADER_RE.match(line)
        if header:
            current = header.group(1).lower()
            if current in seen:
                raise ParseError(f"line {line_no}: section '{header.group(1)}:' appears twice")
            seen.add(current)
            line = header.group(2).strip()  # value on the same line as the header
            if not line:
                continue

        if current is None:
            raise ParseError(f"line {line_no}: text before any section header: {line!r}")
        sections[current].append((line_no, line))

    for name in _SECTIONS:
        if name not in seen:
            raise ParseError(f"missing section '{name.capitalize()}:'")
    return sections


def parse_problem_text(text: str) -> Problem:
    """Parse the contents of a problem file into a Problem."""
    sections = _split_sections(text)
    graph = Graph()

    # --- Nodes ---------------------------------------------------------
    if not sections["nodes"]:
        raise ParseError("the Nodes section is empty")
    for line_no, line in sections["nodes"]:
        match = _NODE_RE.match(line)
        if not match:
            raise ParseError(f"line {line_no}: bad node definition {line!r} "
                             "(expected e.g. '1: (4,1)')")
        node_id, x, y = int(match.group(1)), _to_number(match.group(2)), _to_number(match.group(3))
        try:
            graph.add_node(node_id, x, y)
        except ValueError as exc:
            raise ParseError(f"line {line_no}: {exc}") from None

    # --- Edges ---------------------------------------------------------
    for line_no, line in sections["edges"]:
        match = _EDGE_RE.match(line)
        if not match:
            raise ParseError(f"line {line_no}: bad edge definition {line!r} "
                             "(expected e.g. '(2,1): 4')")
        source, target = int(match.group(1)), int(match.group(2))
        try:
            graph.add_edge(source, target, _to_number(match.group(3)))
        except ValueError as exc:
            raise ParseError(f"line {line_no}: {exc}") from None

    # --- Origin --------------------------------------------------------
    origin_lines = sections["origin"]
    if len(origin_lines) != 1 or not _INTEGER_RE.match(origin_lines[0][1]):
        raise ParseError("the Origin section must contain exactly one node number")
    origin = int(origin_lines[0][1])
    if not graph.has_node(origin):
        raise ParseError(f"line {origin_lines[0][0]}: origin {origin} is not a defined node")

    # --- Destinations (separated by ';') ----------------------------------
    destinations: List[int] = []
    for line_no, line in sections["destinations"]:
        for token in line.split(";"):
            token = token.strip()
            if not token:  # tolerate a trailing ';'
                continue
            if not _INTEGER_RE.match(token):
                raise ParseError(f"line {line_no}: bad destination {token!r}")
            destination = int(token)
            if not graph.has_node(destination):
                raise ParseError(f"line {line_no}: destination {destination} is not a defined node")
            if destination not in destinations:
                destinations.append(destination)
    if not destinations:
        raise ParseError("the Destinations section is empty")

    return Problem(graph, origin, destinations)


def parse_problem_file(path: Union[str, Path]) -> Problem:
    """Read and parse a problem file. OSError propagates if it cannot be read."""
    # utf-8-sig silently drops a byte-order mark if Windows Notepad added one.
    text = Path(path).read_text(encoding="utf-8-sig")
    return parse_problem_text(text)
