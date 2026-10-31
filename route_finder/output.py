"""Formats search results exactly as the assignment specifies.

Success:
    filename method
    goal number_of_nodes
    path

No goal reachable (the brief does not define this case - confirm the format
with the tutor):
    filename method
    No goal is reachable; number_of_nodes
"""

from __future__ import annotations

from .engine import SearchResult

# How consecutive nodes in the path are joined. The brief only says the path
# is "a sequence of moves", so this is a single place to change it.
PATH_SEPARATOR = " -> "


def format_result(filename: str, method: str, result: SearchResult) -> str:
    """Return the three-line output block for one run."""
    lines = [f"{filename} {method}"]
    if result.found:
        lines.append(f"{result.goal} {result.nodes_created}")
        lines.append(PATH_SEPARATOR.join(str(state) for state in result.path))
    else:
        lines.append(f"No goal is reachable; {result.nodes_created}")
    return "\n".join(lines)
