import networkx as nx
from enum import Enum, auto

# TODO: Delete
class Node:
    pass

class State(Enum):
    PENDING = auto()
    RUNNING = auto()
    SKIPPED = auto()
    FAILED = auto()
    SUCCESS = auto()
    UNKNOWN = auto()

class Run(nx.DiGraph):
    def __init__(self):
        pass

class Engine:
    def __init__(self, run: Run):
        sefl.run = run

    def handler(self):
        print("in handler")
        starters = [n for n in run.nodes if run.in_degree(n) == 0]
        for starter in starters:
            starter.run()


