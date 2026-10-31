# COS30019 Assignment 2A - Tree-Based Route Finding

Python implementation of six tree-based search methods (DFS, BFS, GBFS, A*, CUS1, CUS2)
for the Route Finding problem. Written from scratch with the standard library only.

## Run it

Requires Python 3.8 or newer (tested on Windows 11).

    python search.py <filename> <method>
    search <filename> <method>              (Windows, via search.bat)

`<method>` is one of `DFS`, `BFS`, `GBFS`, `AS`, `CUS1`, `CUS2`.

Example:

    > python search.py tests/cases/PathFinder-test.txt BFS
    tests/cases/PathFinder-test.txt BFS
    4 10
    2 -> 1 -> 4

Line 2 is `goal number_of_nodes`; line 3 is the path from origin to goal.
If no destination can be reached, line 2 is `No goal is reachable; number_of_nodes`.

Run the unit tests:

    python -m unittest discover -s tests -v

## Project layout

    search.py                  CLI entry point
    search.bat                 Windows wrapper
    route_finder/
        graph.py               directed weighted graph + coordinates
        problem.py             graph + origin + destinations
        parser.py              reads the problem-file format
        search_node.py         search-tree node (state, parent, g, depth, order)
        frontier.py            stack / queue / priority queue  <- ALL tie-breaking lives here
        engine.py              generic tree-search loop + node counting
        output.py              output formatting
        algorithms/
            dfs.py  bfs.py            Ahmed  (done)
            gbfs.py astar.py cus2.py  Ramy
            cus1.py                   Faisal
            __init__.py               method-name -> function table
    tests/
        test_core.py           unit tests for the core (Ahmed)
        cases/                 problem files for the 15+ test cases (Omar)

## Team conventions (do not change without telling everyone)

1. **Tree search.** No global explored set. A child may not revisit a node already on its own path.
2. **Nodes created** = every node generated and added to the frontier (root included). Children
   skipped by the cycle check are not counted. Create nodes only via `SearchSpace`.
3. **Goal test at expansion** (when a node is popped), for every method.
4. **Tie-breaking** (the marker checks this): lower node number first; then the node added to the
   frontier earlier. Use the frontiers in `frontier.py` - never write your own ordering.
5. **Heuristic** (informed methods): Euclidean distance to the nearest destination, unless the
   tutor says otherwise.

## Adding a method

Edit your own file in `route_finder/algorithms/`. It must expose
`search(problem) -> SearchResult`. See `gbfs.py` for the pattern.

## Status

| Method | Owner | Status |
|---|---|---|
| DFS, BFS | Ahmed | done, tested |
| GBFS, AS, CUS2 | Ramy | done, tested |
| CUS1 | Faisal | stub |
