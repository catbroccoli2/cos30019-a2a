# COS30019 Assignment 2A - Tree-Based Route Finding

Python implementation of six tree-based search methods (DFS, BFS, GBFS, A*, CUS1, CUS2)
for the Route Finding problem. Written from scratch with the standard library only.

## Run it

Requires Python 3.8 or newer. There are no third-party dependencies. All commands are run from the repository root, the folder that contains `search.py`.

### Run a search

    python search.py <filename> <method>
    search <filename> <method>              (Windows only, through search.bat)

`<method>` is one of `DFS`, `BFS`, `GBFS`, `AS` (A*), `CUS1` (iterative-deepening DFS) or `CUS2` (IDA* on number of moves). It is not case-sensitive.

Example:

    > python search.py tests/cases/PathFinder-test.txt BFS
    tests/cases/PathFinder-test.txt BFS
    4 10
    2 -> 1 -> 4

- Line 1 is the file name and method.
- Line 2 is `goal number_of_nodes`.
- Line 3 is the path from the origin to the goal.
- If no destination can be reached, line 2 is `No goal is reachable; number_of_nodes`.
- A malformed problem file prints an error naming the line, and the program exits with a non-zero code.

### Test and benchmark commands

| Command | What it does |
|---|---|
| `python tests/run_all.py` | Runs all six methods on all 20 files in `tests/cases/`. Checks each result against the hand-worked answers in `tests/expected_results.py`, prints PASS or FAIL per row, and writes `results/run_all.csv`. Exits with code 1 if any row fails. Add `--repeat 20` for steadier run times. |
| `python -m unittest discover -s tests` | Runs all 80 unit tests, including the hand-worked results for every test file. |
| `python -m research <file> [auto\|perm\|dp\|ucs]` | Research feature: finds the cheapest walk that visits every destination. The optional last argument picks the solver. The default is `auto`. |
| `python -m research.benchmark [algorithms\|research]` | Regenerates the benchmark CSVs in `results/`, which are the data behind the report. With no argument it runs both. The `algorithms` run takes about 40 seconds. |

Research example:

    > python -m research tests/cases/PathFinder-test.txt
    tests/cases/PathFinder-test.txt RESEARCH (perm)
    visit_order 4 5  total_cost 17
    2 -> 1 -> 4 -> 5