from enum import Enum

import networkx as nx
from rich.padding import Padding
from rich.table import Table
from textual.app import RenderResult
from textual.widgets import Static


class NodeStatus(Enum):
    """Node execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


STATUS_COLORS = {
    NodeStatus.PENDING: "white",
    NodeStatus.RUNNING: "blue",
    NodeStatus.SUCCESS: "green",
    NodeStatus.FAILED: "red",
    NodeStatus.SKIPPED: "yellow",
}

STATUS_SYMBOLS = {
    NodeStatus.PENDING: "○",
    NodeStatus.RUNNING: "◐",
    NodeStatus.SUCCESS: "●",
    NodeStatus.FAILED: "✕",
    NodeStatus.SKIPPED: "⊘",
}


class DAG(Static):
    """Textualize widget for DAG visualization"""

    def __init__(self, digraph: nx.DiGraph):
        super().__init__()
        self.digraph = digraph

    def render(self) -> RenderResult:
        return self.generate_table(self.digraph)

    def generate_table(self, dag: nx.DiGraph):
        # topological layers (generations)
        gens = list(nx.topological_generations(dag))
        layers = [sorted(g) for g in gens]
        if not layers:
            return Table.grid()

        # columns: layer columns separated by connector columns
        n_layers = len(layers)
        n_cols = n_layers * 2 - 1
        table = Table.grid()
        for _ in range(n_cols):
            table.add_column("")
        max_rows = max(len(layer) for layer in layers)

        # grid of cells
        grid = [["" for _ in range(n_cols)] for _ in range(max_rows)]
        positions = {}
        # place nodes in even columns (0,2,4,...)
        for li, layer in enumerate(layers):
            col = li * 2
            for ri, node in enumerate(layer):
                positions[node] = (col, ri)
                status = dag.nodes[node].get("status", NodeStatus.PENDING)
                color = STATUS_COLORS.get(status, "white")
                symbol = STATUS_SYMBOLS.get(status, "○")
                # color the symbol; keep name at right
                grid[ri][col] = Padding(
                    f"[{color}]{symbol}[/]{' '}{node}", (0, 1, 0, 1)
                )

        for generation in gens:
            all_predecessors = []
            for node in generation:
                all_predecessors.extend(list(dag.predecessors(node)))
            all_predecessors = list(set(all_predecessors))

        # add rows to table
        for r in range(max_rows):
            row_cells = []
            for c in range(n_cols):
                cell = grid[r][c]
                row_cells.append(cell if cell != "" else "")
            table.add_row(*row_cells)
        return table
