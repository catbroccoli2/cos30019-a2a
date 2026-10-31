# Working together

## Who owns what

| Person | Files you edit |
|---|---|
| A | `search.py`, `search.bat`, `route_finder/{graph,problem,parser,search_node,frontier,engine,output}.py`, `algorithms/{dfs,bfs}.py` |
| B | `algorithms/{gbfs,astar,cus2}.py`, new `route_finder/heuristics.py` |
| C | `algorithms/cus1.py`, research code (put it in `research/`) |
| D | `tests/cases/*.txt`, `tests/run_all.py` (batch runner), report compilation |

Need a change in a file you do not own (for example the frontier)? Message the owner or open a
pull request and tag them. This avoids merge conflicts and keeps tie-breaking in one place.

## Git workflow

1. `git pull` on `main` before you start.
2. Make your own branch: `git checkout -b b/informed-search` (use your letter as the prefix).
3. Commit small and often, with clear messages ("Add Euclidean heuristic", not "update").
4. Push your branch and open a pull request into `main`. Person A reviews and merges.
5. Never commit directly to `main` and never force-push.

Commit under your own name so the contribution statement is easy to back up:

    git config user.name "Your Full Name"
    git config user.email "your.email@example.com"

## Code standards (up to -10 marks if ignored)

* Every module, class and function has a docstring saying what it does.
* Comments explain *why*, not what. No dead or commented-out code.
* Descriptive names, small functions, no copy-pasted blocks.
* Standard library only. No search or graph libraries.
* Run `python -m unittest discover -s tests` before every push.

## Cross-review

Each person reviews one other person's algorithm against the tie-breaking rules:
A reviews B, B reviews A, C reviews D, D reviews C. Use the checklist in the PR description.
