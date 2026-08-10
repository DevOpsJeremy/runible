import networkx as nx

graph = nx.DiGraph()

graph.add_edges_from([
    ("checkout", "build"),
    ("build", "test"),
    ("build", "lint"),
    ("test", "deploy"),
    ("lint", "deploy"),
])

graph.nodes["build"]["label"] = "Build"
graph.nodes["build"]["status"] = "running"
graph.nodes["build"]["duration"] = "42s"

