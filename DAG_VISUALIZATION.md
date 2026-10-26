# DAG Visualization with Textualize

A beautiful, interactive DAG (Directed Acyclic Graph) visualization tool built with [Textualize](https://textual.textualize.io/) and [Rich](https://rich.readthedocs.io/).

## Features

- 🎨 **Beautiful Terminal UI** - Rendered with Textualize and Rich
- 📊 **Interactive Visualization** - Tree-based DAG display with status indicators
- 🎯 **Status Tracking** - Visual status symbols for nodes (pending, running, success, failed, skipped)
- 🔄 **Dependency Graph** - Clear visualization of task dependencies
- 📈 **Real-time Updates** - Monitor workflow execution
- 🎪 **Graceful Fallback** - Works even without Textualize (text-based output)

## Status Symbols

| Symbol | Status | Color |
|--------|--------|-------|
| ○ | Pending | White |
| ◐ | Running | Blue (blinking) |
| ● | Success | Green |
| ✕ | Failed | Red |
| ⊘ | Skipped | Yellow |

## Installation

### Basic Usage (No External Dependencies)

The script includes a fallback mode that works without Textual:

```bash
python dag_viz_textualize.py
```

### Full Textualize UI

For the interactive terminal UI, install Textualize:

```bash
python -m pip install textual
```

Then run:

```bash
python dag_viz_textualize.py
```

## Quick Start

### 1. Basic Example

```python
from dag_viz_textualize import SimpleDAG, NodeStatus, DAGApp

# Create a DAG
dag = SimpleDAG()

# Add edges (automatically creates nodes)
dag.add_edge("Task A", "Task B")
dag.add_edge("Task B", "Task C")
dag.add_edge("Task B", "Task D")

# Set node statuses
statuses = {
    "Task A": NodeStatus.SUCCESS,
    "Task B": NodeStatus.RUNNING,
    "Task C": NodeStatus.PENDING,
    "Task D": NodeStatus.PENDING,
}

# Run the app
app = DAGApp(dag, statuses)
app.run()
```

### 2. CI/CD Pipeline Example

```python
from dag_viz_textualize import SimpleDAG, NodeStatus, DAGApp

dag = SimpleDAG()

# Define CI/CD workflow
edges = [
    ("Checkout", "Install"),
    ("Install", "Lint"),
    ("Install", "Build"),
    ("Lint", "Test"),
    ("Build", "Test"),
    ("Test", "Deploy"),
]

for from_node, to_node in edges:
    dag.add_edge(from_node, to_node)

statuses = {
    "Checkout": NodeStatus.SUCCESS,
    "Install": NodeStatus.SUCCESS,
    "Lint": NodeStatus.SUCCESS,
    "Build": NodeStatus.RUNNING,
    "Test": NodeStatus.PENDING,
    "Deploy": NodeStatus.PENDING,
}

app = DAGApp(dag, statuses)
app.run()
```

## API Reference

### SimpleDAG

Simple in-memory DAG implementation.

#### Methods

- `add_node(name: str, dependencies: List[str] = None)` - Add a node
- `add_edge(from_node: str, to_node: str)` - Add an edge
- `get_root_nodes() -> List[str]` - Get nodes with no dependencies
- `get_successors(node: str) -> List[str]` - Get nodes that depend on this node
- `get_all_nodes() -> List[str]` - Get all node names

### NodeStatus

Enum for node execution status:

- `PENDING` - Waiting to execute
- `RUNNING` - Currently executing
- `SUCCESS` - Completed successfully
- `FAILED` - Failed during execution
- `SKIPPED` - Skipped (not executed)

### DAGApp

Textualize app for rendering the DAG.

#### Constructor

```python
DAGApp(dag: SimpleDAG, node_statuses: Dict[str, NodeStatus] = None)
```

#### Keybindings

- `q` - Quit
- `r` - Refresh display

## Advanced Examples

### Example 1: Data Processing Pipeline

See `dag_viz_example.py` for a complete data pipeline example.

### Example 2: Custom Styling

```python
from dag_viz_textualize import SimpleDAG, NodeStatus, DAGApp

dag = SimpleDAG()
dag.add_edge("Start", "Process")
dag.add_edge("Process", "End")

statuses = {
    "Start": NodeStatus.SUCCESS,
    "Process": NodeStatus.RUNNING,
    "End": NodeStatus.PENDING,
}

app = DAGApp(dag, statuses)
app.run()
```

### Example 3: Dynamic Status Updates

Create a custom app that updates statuses:

```python
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.containers import Vertical, Horizontal
import asyncio

from dag_viz_textualize import SimpleDAG, NodeStatus, DAGRenderer, DAGStatusTable


class DynamicDAGApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="dag_container"):
                self.dag_renderer = DAGRenderer(self.dag, self.statuses)
                yield self.dag_renderer
            with Vertical(id="status_container"):
                self.status_table = DAGStatusTable(self.statuses)
                yield self.status_table
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(2, self.update_status)

    def update_status(self) -> None:
        # Update statuses here
        self.statuses["Task"] = NodeStatus.RUNNING
        self.dag_renderer.node_statuses = self.statuses
        self.status_table.node_statuses = self.statuses
        self.refresh()
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `r` | Refresh the display |

## Output Modes

### Interactive Mode (with Textualize)

Shows:
- Left panel: Tree-based DAG visualization
- Right panel: Status table with node information
- Header: Application title and controls
- Footer: Available keyboard shortcuts

### Text Mode (without Textualize)

Shows:
- DAG structure in text format
- Node relationships (dependencies → dependents)
- Status for each node

## Performance

- **Nodes**: Tested with 1000+ nodes
- **Edges**: Handles complex dependency graphs
- **Rendering**: Real-time updates with minimal latency
- **Memory**: Efficient in-memory representation

## Customization

### Custom Node Data

You can extend `SimpleDAG` to store additional node metadata:

```python
from dag_viz_textualize import SimpleDAG


class ExtendedDAG(SimpleDAG):
    def __init__(self):
        super().__init__()
        self.node_metadata = {}

    def add_node_with_metadata(self, name: str, metadata: dict):
        self.add_node(name)
        self.node_metadata[name] = metadata
```

### Custom Colors and Symbols

Edit the `STATUS_COLORS` and `STATUS_SYMBOLS` dicts:

```python
from dag_viz_textualize import DAGRenderer, STATUS_COLORS, STATUS_SYMBOLS, NodeStatus

# Customize symbols
STATUS_SYMBOLS[NodeStatus.RUNNING] = "▶"
STATUS_SYMBOLS[NodeStatus.SUCCESS] = "✓"
STATUS_SYMBOLS[NodeStatus.FAILED] = "✗"
```

## Troubleshooting

### "Textual not available" warning

Install Textualize:

```bash
python -m pip install textual
```

The script will still work in text-mode fallback without it.

### DAG not rendering correctly

Ensure:
1. All nodes have unique names
2. No circular dependencies (DAGs must be acyclic)
3. Status keys match node names exactly

### Performance issues with large DAGs

For very large DAGs (1000+ nodes):
1. Use the text-mode fallback (no Textualize)
2. Consider filtering/grouping nodes
3. Use pagination in custom implementations

## Files

- `dag_viz_textualize.py` - Main visualization module
- `dag_viz_example.py` - Example implementations and workflows

## License

MIT - See repository for details

## See Also

- [Textualize](https://textual.textualize.io/) - TUI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful formatting
- [NetworkX](https://networkx.org/) - Graph library (optional)
