"""
DAG Visualization using Textualize for beautiful terminal UI.
Simple implementation without external DAG library dependencies.
"""

from dataclasses import dataclass
from enum import Enum


class NodeStatus(Enum):
    """Node execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """Represents a node in the DAG."""

    name: str
    dependencies: list[str]


class SimpleDAG:
    """Simple DAG implementation without networkx dependency."""

    def __init__(self):
        self.nodes: dict[str, DAGNode] = {}
        self.edges: dict[str, list[str]] = {}

    def add_node(self, name: str, dependencies: list[str] | None = None) -> None:
        """Add a node to the DAG."""
        deps = dependencies or []
        self.nodes[name] = DAGNode(name, deps)
        if name not in self.edges:
            self.edges[name] = []

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add an edge from one node to another."""
        if from_node not in self.nodes:
            self.add_node(from_node)
        if to_node not in self.nodes:
            self.add_node(to_node)

        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)

        # Update dependencies for to_node
        self.nodes[to_node].dependencies.append(from_node)

    def get_root_nodes(self) -> list[str]:
        """Get all nodes with no dependencies."""
        return [name for name, node in self.nodes.items() if not node.dependencies]

    def get_successors(self, node: str) -> list[str]:
        """Get all nodes that depend on the given node."""
        return self.edges.get(node, [])

    def get_all_nodes(self) -> list[str]:
        """Get all node names."""
        return list(self.nodes.keys())


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

try:
    from io import StringIO

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Header, Static

    class DAGRenderer(Static):
        """Widget to render a DAG as a horizontal pipeline."""

        def __init__(
            self,
            dag: SimpleDAG,
            node_statuses: dict[str, NodeStatus] | None = None,
            **kwargs,
        ):
            super().__init__(**kwargs)
            self.dag = dag
            self.node_statuses = node_statuses or {}
            # Set default status to PENDING for nodes without status
            for node in self.dag.get_all_nodes():
                if node not in self.node_statuses:
                    self.node_statuses[node] = NodeStatus.PENDING

        def _calculate_stages(self) -> dict[int, list[str]]:
            """Calculate topological stages for horizontal layout."""
            stages = {}
            node_levels = {}

            # Calculate the level of each node based on dependencies
            def get_level(node: str) -> int:
                if node in node_levels:
                    return node_levels[node]

                deps = self.dag.nodes[node].dependencies
                if not deps:
                    level = 0
                else:
                    level = max(get_level(dep) for dep in deps) + 1

                node_levels[node] = level
                return level

            # Calculate levels for all nodes
            for node in self.dag.get_all_nodes():
                level = get_level(node)
                if level not in stages:
                    stages[level] = []
                stages[level].append(node)

            # Sort nodes within each stage for consistency
            for level in stages:
                stages[level].sort()

            return stages

        def render(self) -> Panel:
            """Render the DAG as a horizontal pipeline with table-based alignment."""
            stages = self._calculate_stages()

            if not stages:
                return Panel("Empty DAG", title="[bold blue]Pipeline[/bold blue]")

            # Calculate positions for each node
            max_height = max(len(nodes) for nodes in stages.values())
            node_positions = {}  # (stage_idx, node_name) -> row_idx

            for stage_idx in sorted(stages.keys()):
                nodes_in_stage = stages[stage_idx]
                num_nodes = len(nodes_in_stage)

                if num_nodes == 1:
                    # Center single node
                    row_idx = max_height // 2
                    node_positions[(stage_idx, nodes_in_stage[0])] = row_idx
                else:
                    # Distribute multiple nodes evenly
                    total_space = max_height - 1 if max_height > 1 else 1
                    for i, node in enumerate(nodes_in_stage):
                        row_idx = (
                            round(i * total_space / (num_nodes - 1))
                            if num_nodes > 1
                            else 0
                        )
                        node_positions[(stage_idx, node)] = row_idx

            # Build grid: [row][column] where columns alternate between stage nodes and connectors
            grid_width = len(stages) * 2 - 1  # stages + connectors between them
            grid = [[Text("") for _ in range(grid_width)] for _ in range(max_height)]

            # Fill in stage nodes
            for stage_idx in sorted(stages.keys()):
                col_idx = stage_idx * 2
                nodes_in_stage = stages[stage_idx]

                for node in nodes_in_stage:
                    row_idx = node_positions[(stage_idx, node)]
                    status = self.node_statuses.get(node, NodeStatus.PENDING)
                    symbol = STATUS_SYMBOLS[status]
                    color = STATUS_COLORS[status]
                    node_text = Text(f"{symbol} {node}", style=f"bold {color}")
                    grid[row_idx][col_idx] = node_text

            # Fill in connectors between stages
            for stage_idx in sorted(stages.keys())[:-1]:
                connector_col = stage_idx * 2 + 1
                current_nodes = stages[stage_idx]
                next_nodes = stages[stage_idx + 1]

                # Get positions of current and next nodes
                current_rows = set(
                    node_positions[(stage_idx, n)] for n in current_nodes
                )
                next_rows = set(node_positions[(stage_idx + 1, n)] for n in next_nodes)

                # Draw connectors
                for row_idx in range(max_height):
                    if row_idx in current_rows and row_idx in next_rows:
                        # Straight connection
                        grid[row_idx][connector_col] = Text("─", style="dim cyan")
                    elif row_idx in current_rows:
                        # Node on left, arc down or up
                        min_next = min(next_rows)
                        if row_idx < min_next:
                            grid[row_idx][connector_col] = Text("╭", style="dim cyan")
                        else:
                            grid[row_idx][connector_col] = Text("╰", style="dim cyan")
                    elif row_idx in next_rows:
                        # Node on right, arc down or up
                        min_current = min(current_rows)
                        if row_idx < min_current:
                            grid[row_idx][connector_col] = Text("╭", style="dim cyan")
                        else:
                            grid[row_idx][connector_col] = Text("╰", style="dim cyan")
                    else:
                        # Between nodes, draw vertical line
                        min_curr = min(current_rows)
                        max_curr = max(current_rows)
                        min_next = min(next_rows)
                        max_next = max(next_rows)

                        all_rows = set(
                            range(min(min_curr, min_next), max(max_curr, max_next) + 1)
                        )
                        if row_idx in all_rows:
                            # Determine if we need T-junction or vertical
                            connects_current = any(
                                curr_row == row_idx
                                or (
                                    min(curr_row, row_idx)
                                    < row_idx
                                    < max(curr_row, row_idx)
                                    and min_curr <= row_idx <= max_curr
                                )
                                for curr_row in current_rows
                            )
                            connects_next = any(
                                next_row == row_idx
                                or (
                                    min(next_row, row_idx)
                                    < row_idx
                                    < max(next_row, row_idx)
                                    and min_next <= row_idx <= max_next
                                )
                                for next_row in next_rows
                            )

                            if (min_curr <= row_idx <= max_curr) or (
                                min_next <= row_idx <= max_next
                            ):
                                grid[row_idx][connector_col] = Text(
                                    "│", style="dim cyan"
                                )

            # Convert grid to text
            lines = []
            for row in grid:
                line_parts = []
                for cell in row:
                    if isinstance(cell, Text):
                        line_parts.append(cell)
                    else:
                        line_parts.append(Text(str(cell)))
                lines.append(Text(" ").join(line_parts))

            output = Text("\n").join(lines)

            panel = Panel(
                output,
                title="[bold blue]CI/CD Pipeline[/bold blue]",
                expand=True,
                border_style="cyan",
            )
            return panel

    class DAGStatusTable(Static):
        """Widget to display node statuses in a table."""

        def __init__(self, node_statuses: dict[str, NodeStatus], **kwargs):
            super().__init__(**kwargs)
            self.node_statuses = node_statuses

        def render(self) -> Panel:
            """Render the status table."""
            table = Table(
                title="Node Status", show_header=True, header_style="bold magenta"
            )
            table.add_column("Node", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Symbol", justify="center")

            for node, status in self.node_statuses.items():
                symbol = STATUS_SYMBOLS[status]
                color = STATUS_COLORS[status]
                table.add_row(
                    node,
                    Text(status.value, style=f"bold {color}"),
                    Text(symbol, style=f"bold {color}"),
                )

            return Panel(
                table, title="[bold green]Status Overview[/bold green]", expand=True
            )

    class DAGApp(App):
        """Textualize app for DAG visualization."""

        CSS = """
        Screen {
            layout: vertical;
        }

        #dag_container {
            height: 60%;
            width: 100%;
        }

        #status_container {
            height: 40%;
            width: 100%;
        }

        DAGRenderer {
            overflow: auto;
        }

        DAGStatusTable {
            overflow: auto;
        }
        """

        BINDINGS = [
            ("q", "quit", "Quit"),
            ("r", "refresh", "Refresh"),
        ]

        def __init__(
            self, dag: SimpleDAG, node_statuses: dict[str, NodeStatus] | None = None
        ):
            super().__init__()
            self.dag = dag
            self.initial_statuses = node_statuses or {}

        def compose(self) -> ComposeResult:
            """Create child widgets for the app."""
            yield Header()

            with Horizontal():
                with Vertical(id="dag_container"):
                    yield DAGRenderer(self.dag, self.initial_statuses)

                with Vertical(id="status_container"):
                    yield DAGStatusTable(self.initial_statuses)

            yield Footer()

        def action_refresh(self) -> None:
            """Refresh the display."""
            self.refresh()

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    print("⚠️  Textual not available. Install with: python -m pip install textual")


def create_example_dag() -> tuple[SimpleDAG, dict[str, NodeStatus]]:
    """Create an example DAG."""
    dag = SimpleDAG()

    # Create edges for a typical CI/CD pipeline
    edges = [
        ("Checkout", "Install"),
        ("Install", "Lint"),
        ("Install", "Build"),
        ("Lint", "Test"),
        ("Build", "Test"),
        ("Test", "Deploy"),
        ("Test", "Documentation"),
        ("Deploy", "Monitor"),
        ("Documentation", "Release"),
    ]

    for from_node, to_node in edges:
        dag.add_edge(from_node, to_node)

    # Set some example statuses
    statuses = {
        "Checkout": NodeStatus.SUCCESS,
        "Install": NodeStatus.SUCCESS,
        "Lint": NodeStatus.SUCCESS,
        "Build": NodeStatus.RUNNING,
        "Test": NodeStatus.PENDING,
        "Deploy": NodeStatus.PENDING,
        "Documentation": NodeStatus.PENDING,
        "Monitor": NodeStatus.PENDING,
        "Release": NodeStatus.PENDING,
    }

    return dag, statuses


if __name__ == "__main__":
    dag, statuses = create_example_dag()

    if HAS_TEXTUAL:
        app = DAGApp(dag, statuses)
        app.run()
    else:
        # Fallback: Print DAG in text format
        print("\n📊 DAG Structure:")
        print("=" * 50)

        for node in dag.get_all_nodes():
            status = statuses.get(node, NodeStatus.PENDING)
            symbol = STATUS_SYMBOLS[status]
            color_name = STATUS_COLORS[status]

            deps = dag.nodes[node].dependencies
            deps_str = f" ← {', '.join(deps)}" if deps else ""
            children = dag.get_successors(node)
            children_str = f" → {', '.join(children)}" if children else ""

            print(f"{symbol} {node}{deps_str}{children_str}")
            print(f"   Status: {status.value}")

        print("=" * 50)
