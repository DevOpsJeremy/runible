# Horizontal CI/CD Pipeline Visualization ✨

Updated the DAG visualization to display as a **left-to-right pipeline** instead of a folder-tree structure!

## What Changed

### Before (Tree Layout)
```
📊 DAG Execution Graph
├── ● Checkout
│   ├── ● Install
│   │   ├── ● Lint
│   │   │   └── ○ Test
│   │   └── ◐ Build
│   │       └── ○ Test
│   └── ...
```

### After (Horizontal Pipeline Layout) ✅
```
● Checkout  →  ● Install  →  ● Lint  →  ◐ Test  →  ○ Deploy  →  ○ Release
                           →  ◐ Build  →
```

## Key Features

### 1. **Left-to-Right Flow**
Stages flow naturally from left to right, just like CI/CD pipelines

### 2. **Vertical Distribution**
- **Single nodes** at a stage: Centered vertically
- **Multiple nodes** at a stage: Evenly distributed vertically

Example with parallel tests:
```
              →  ● UnitTests  →              
● Setup  →  ◐ IntegrationTests  →  ○ Report  →  ○ Deploy
              →  ◐ E2ETests  →
```

### 3. **Arrow Connectors**
Stages connected with arrows (→) for clear flow visualization

### 4. **Status Symbols**
- `●` SUCCESS (green)
- `◐` RUNNING (blue, blinking)
- `○` PENDING (white)
- `✕` FAILED (red)
- `⊘` SKIPPED (yellow)

## How It Works

### Stage Calculation
The visualization uses **topological sorting** to determine stages:
- **Level 0**: Nodes with no dependencies (start nodes)
- **Level 1**: Nodes that depend only on level 0 nodes
- **Level N**: Nodes that depend on level N-1 nodes

```
Stage 0: Source
         ↓
Stage 1: Lint, Build        (2 nodes → distributed vertically)
         ↓
Stage 2: Test               (1 node → centered)
         ↓
Stage 3: Staging, Docs      (2 nodes → distributed vertically)
         ↓
Stage 4: Smoke, Publish     (2 nodes → distributed vertically)
         ↓
Stage 5: Production         (1 node → centered)
```

### Vertical Alignment

For a stage with N nodes and max_height H:

**Single Node:**
```
        [Centered at height H/2]
```

**Multiple Nodes (evenly distributed):**
```
[Node 1 at height 0]
[Node 2 at height H/3]
[Node 3 at height 2H/3]
```

## Examples

### Simple Linear Pipeline
```
● Checkout  →  ● Build  →  ◐ Test  →  ○ Deploy
```

### Parallel Testing
```
              →  ● UnitTests  →              
● Setup  →  ◐ IntegrationTests  →  ○ Report  →  ○ Deploy
              →  ◐ E2ETests  →
```

### Complex Multi-Branch
```
              →  ● Build  →                   →  ◐ Docs  →  ○ Publish  →              
● Source  →  ● Lint  →  ● Test  →  ◐ Staging  →  ○ Smoke  →  ○ Production
```

## Files Updated

### Core Module
- **`dag_viz_textualize.py`**
  - Updated `DAGRenderer.render()` to use horizontal layout
  - Added `_calculate_stages()` for topological ordering
  - Fixed positioning logic for single vs. multiple nodes

### New Demo
- **`dag_viz_demo.py`** - Beautiful demonstrations with:
  - Simple linear pipeline
  - Parallel tests stage
  - Complex multi-branch flow
  - Text rendering (works without Textual)

## Usage

### Run Demonstrations
```bash
python dag_viz_demo.py
```

### Create Custom Pipeline
```python
from dag_viz_textualize import SimpleDAG, NodeStatus, DAGApp

dag = SimpleDAG()
dag.add_edge("Checkout", "Build")
dag.add_edge("Build", "Test")
dag.add_edge("Test", "Deploy")

statuses = {
    "Checkout": NodeStatus.SUCCESS,
    "Build": NodeStatus.SUCCESS,
    "Test": NodeStatus.RUNNING,
    "Deploy": NodeStatus.PENDING,
}

app = DAGApp(dag, statuses)
app.run()  # Full Textualize UI
```

## Installation & Running

### No Dependencies Required
```bash
# Works with just Python stdlib
python dag_viz_textualize.py
```

### With Textualize (Full UI)
```bash
python -m pip install textual rich
python dag_viz_textualize.py
```

## Implementation Details

### Algorithm
1. **Calculate levels** - Recursive topological sort
   - Level 0: Nodes with no dependencies
   - Level N: max(dependencies) + 1

2. **Group by stage** - Collect all nodes at each level

3. **Calculate positions** - For each row in output:
   - If single node: center it (row = max_height / 2)
   - If multiple nodes: distribute evenly using linear interpolation

4. **Render** - Generate text lines connecting stages

### Complexity
- Time: O(V + E) for topological sort
- Space: O(V) for stage storage
- Works efficiently with 1000+ nodes

## Comparison

| Aspect | Tree Layout | Horizontal Pipeline |
|--------|------------|---------------------|
| Flow Direction | Down & Right | Left to Right ✓ |
| Parallel Nodes | Nested vertically | Evenly distributed ✓ |
| Single Nodes | Various heights | Centered ✓ |
| CI/CD Clarity | Poor | Excellent ✓ |
| Arrow Connectors | Implicit | Explicit ✓ |
| Visual Alignment | Loose | Precise ✓ |

## Next Steps

- ✅ Horizontal left-to-right layout
- ✅ Vertical distribution of parallel nodes
- ✅ Centered single nodes
- 🔄 Consider: Interactive navigation with arrow keys
- 🔄 Consider: Zoom/filter by stage
- 🔄 Consider: Real-time status updates

## Testing

```bash
# Test all examples
python dag_viz_demo.py

# Test with Runible workflows
python dag_viz_runible.py simple
python dag_viz_runible.py parallel
python dag_viz_runible.py conditional
```

---

**Status:** ✅ Horizontal pipeline layout complete and tested!
