import queue
from enum import Enum

import networkx as nx
from rich.padding import Padding
from textual.app import App, ComposeResult, RenderResult
from textual.widgets import DataTable, Footer, Header
from textual.containers import Container
from textual.binding import Binding

from ..engine import RunBase
from ..interface import Interface


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


class DAGApp(App):
    def __init__(self, message_queue: queue.Queue = None):
        super().__init__()
        self.message_queue = message_queue
        self.dag_widget = None

    def on_mount(self):
        self.set_interval(0.1, self._process_messages)

    def _process_message(self):
        try:
            while True:
                msg = self.message_queue.get_nowait()
        except queue.Empty:
            pass

    def new_digraph(self):
        dg = nx.DiGraph()
        dg.add_node("node_a", status=NodeStatus.SUCCESS)
        dg.add_node("node_b", status=NodeStatus.FAILED)
        dg.add_node("node_c", status=NodeStatus.RUNNING)
        dg.add_node("node_d", status=NodeStatus.PENDING)
        dg.add_node("node_e", status=NodeStatus.PENDING)
        dg.add_node("node_f", status=NodeStatus.PENDING)
        dg.add_node("node_g", status=NodeStatus.PENDING)
        dg.add_node("node_h", status=NodeStatus.PENDING)
        dg.add_node("node_i", status=NodeStatus.PENDING)
        dg.add_node("node_j", status=NodeStatus.PENDING)
        dg.add_node("node_k", status=NodeStatus.PENDING)
        dg.add_node("node_l", status=NodeStatus.PENDING)

        dg.add_edge("node_a", "node_b")
        dg.add_edge("node_a", "node_c")
        dg.add_edge("node_a", "node_h")
        dg.add_edge("node_a", "node_f")
        dg.add_edge("node_a", "node_i")
        dg.add_edge("node_i", "node_l")
        dg.add_edge("node_b", "node_e")
        dg.add_edge("node_b", "node_d")
        dg.add_edge("node_c", "node_e")
        dg.add_edge("node_c", "node_d")
        dg.add_edge("node_h", "node_e")
        dg.add_edge("node_h", "node_d")
        dg.add_edge("node_e", "node_g")
        dg.add_edge("node_e", "node_m")
        dg.add_edge("node_f", "node_g")
        dg.add_edge("node_f", "node_m")
        dg.add_edge("node_j", "node_k")
        return dg

    def compose(self) -> ComposeResult:
        yield Header()
        dag = self.new_digraph()
        self.dag_widget = DAGWidget(digraph=dag)
        yield self.dag_widget
        yield Footer()


class DAGWidget(Container):
    """Textualize widget for DAG visualization"""

    def __init__(self, digraph: nx.DiGraph):
        super().__init__()
        self.digraph = digraph
        self.selected_node = None

    def compose(self) -> ComposeResult:
        table = DataTable()
        table.id = "dag_table"
        yield table

    def on_mount(self):
        table = self.query_one("#dag_table", DataTable)
        self._populate_table(table)
        table.focus()

    def old_populate_table(self, table: DataTable):
        table.add_column("Node", key="node")
        table.add_column("Status", key="status")
        table.add_column("Details", key="details")

        for node, data in self.digraph.nodes(data=True):
            status = data.get("status", NodeStatus.PENDING)
            color = STATUS_COLORS.get(status, "white")
            symbol = STATUS_SYMBOLS.get(status, "○")

            table.add_row(
                node,
                f"[{color}]{symbol} {status.value}[/]",
                f"Predecessors: {list(self.digraph.predecessors(node))}",
            )

    # def render(self) -> RenderResult:
    #     return self.generate_table(self.digraph)

    def _populate_table(self, table: DataTable):
        # topological layers (generations)
        gens = list(nx.topological_generations(self.digraph))
        layers = [sorted(g) for g in gens]
        if not layers:
            return

        # columns: layer columns separated by connector columns
        n_layers = len(layers)
        n_cols = n_layers * 2 - 1
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
                status = self.digraph.nodes[node].get("status", NodeStatus.PENDING)
                color = STATUS_COLORS.get(status, "white")
                symbol = STATUS_SYMBOLS.get(status, "○")
                # color the symbol; keep name at right
                grid[ri][col] = Padding(
                    f"[{color}]{symbol}[/]{' '}{node}", (0, 1, 0, 1)
                )

        for generation in gens:
            all_predecessors = []
            for node in generation:
                all_predecessors.extend(list(self.digraph.predecessors(node)))
            all_predecessors = list(set(all_predecessors))

        # add rows to table
        for r in range(max_rows):
            row_cells = []
            for c in range(n_cols):
                cell = grid[r][c]
                row_cells.append(cell if cell != "" else "")
            table.add_row(*row_cells)
        return table


class WorkflowInterface(Interface):
    def initialize(self, sender: RunBase):
        self.app = DAGApp(message_queue=self.message_queue)
        self.app.run()


if __name__ == "__main__":
    WorkflowInterface().initialize(None)
