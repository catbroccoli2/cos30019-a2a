"""COS30019 Assignment 2A - tree-based search for the Route Finding problem.

Package layout
--------------
graph.py        Directed, weighted graph with 2D node coordinates.
problem.py      A search problem: graph + origin + destination set.
parser.py       Reads the assignment's problem-file format.
search_node.py  A node in the search tree (state, parent, g, depth, order).
frontier.py     Frontier data structures (stack / queue / priority queue).
                ALL tie-breaking rules live here.
engine.py       The generic tree-search loop and node counting.
algorithms/     One module per method: DFS, BFS, GBFS, AS, CUS1, CUS2.
output.py       Formats results exactly as the assignment specifies.

Everything is written from scratch using only the Python standard library.
"""
