"""Research extension (Person C): visit ALL destinations with the shortest total walk.

    python -m research <problem file> [auto|perm|dp|ucs]

Modules:
    distances   Dijkstra and the pairwise shortest-distance table
    orderings   three ways of choosing the best order to visit the destinations
    visit_all   the public entry point that stitches the best walk together
    graphgen    random problem generator (tests and benchmarks)
    benchmark   scaling experiments that write CSV files into results/
"""
