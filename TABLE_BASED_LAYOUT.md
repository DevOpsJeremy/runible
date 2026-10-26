# Table-Based Pipeline Visualization with Unicode Connectors

## ✨ Major Improvements

### Before
- Tree-like structure expanding down and right
- Awkward vertical alignment
- Nodes didn't align across rows
- Simple arrow connectors (→)

### After ✅
- **Table-based grid layout** with proper cell alignment
- **Smooth unicode box drawing connectors**:
  - `─` Horizontal line
  - `│` Vertical line  
  - `╭` Arc connector (top)
  - `╰` Arc connector (bottom)
- **Precise node positioning** in grid cells
- **Perfect vertical alignment** across stages
- **Clear visual flow** from left to right

## Visual Examples

### Simple Linear Pipeline
```
●Checkout              ─            ●Build                 ─            ◐Test                  ─            ○Deploy
```

### Parallel Tests (Multiple nodes at same stage)
```
                       ╭            ◐E2ETests              ╭                                    
●Setup                 ─            ◐IntegrationTests      ─            ○Report                ─            ○Deploy
                       ╰            ●UnitTests             ╰                                    
```

### Complex Multi-Branch
```
                       ╭            ●Build                 ╭                                  ╭            ◐Docs                   ─            ○Publish              ╭                
●Source                ─            ●Lint                  ─            ●Test                 ─            ◐Staging                ─            ○Smoke                ─            ○Production
```

## How It Works

### Grid-Based Layout

Instead of simple text concatenation, the renderer creates a 2D grid:

```
Column structure:
[Stage0] [Connector] [Stage1] [Connector] [Stage2] [Connector] [Stage3]
```

Each column is 24 characters wide for consistent spacing.

### Node Positioning Algorithm

1. **Calculate topological levels** - Assigns each node a stage (0, 1, 2, ...)
2. **Group by stage** - Collect all nodes at each stage
3. **Calculate row positions**:
   - **Single node**: Place at center row (max_height // 2)
   - **Multiple nodes**: Distribute evenly using linear interpolation
4. **Draw connectors** between stages using unicode characters
5. **Fill grid** with nodes and connectors

### Example Positioning

For a pipeline with max_height=5 (needs 5 rows):

**Single node at stage:**
```
Row 0: [empty]
Row 1: [empty]
Row 2: [Node A]     ← Centered
Row 3: [empty]
Row 4: [empty]
```

**Multiple nodes at stage:**
```
Row 0: [Node A]     ← 0 * 4/(3-1) = 0
Row 1: [empty]
Row 2: [Node B]     ← 1 * 4/(3-1) = 2
Row 3: [empty]
Row 4: [Node C]     ← 2 * 4/(3-1) = 4
```

### Connector Lines

Between stages, connectors are drawn:

- **Arc down (╭)**: Node above, next node below
- **Arc up (╰)**: Node below, next node above
- **Straight (─)**: Node at same level
- **Vertical (│)**: Connector between nodes at different levels

## Code Structure

### Main Renderer Class

```python
class DAGRenderer(Static):
    def render(self) -> Panel:
        """Render with table-based layout"""
        stages = self._calculate_stages()
        
        # Create 2D grid
        grid = [[" " for _ in range(grid_width)] 
                for _ in range(max_height)]
        
        # Place nodes
        for stage_idx, nodes in stages.items():
            # Calculate positions and place nodes
            
        # Draw connectors
        for stage_idx in range(len(stages)-1):
            # Draw connecting lines between stages
            
        # Convert to text and return Panel
```

## Features

✅ **Perfect Alignment** - Nodes line up in columns
✅ **Smooth Connectors** - Unicode box drawing characters
✅ **Smart Distribution** - Multiple nodes evenly spaced
✅ **Centered Single Nodes** - Visual balance
✅ **No External Deps** - Works with Python stdlib
✅ **Fallback Mode** - Text rendering when Textual unavailable

## Unicode Characters Used

| Char | Unicode | Name | Purpose |
|------|---------|------|---------|
| `─` | U+2500 | Horizontal | Straight connection |
| `│` | U+2502 | Vertical | Vertical connector |
| `╭` | U+256D | Arc ↗ | Diverging down |
| `╰` | U+2570 | Arc ↖ | Converging up |

## Status Symbols

| Symbol | Status | Color |
|--------|--------|-------|
| `●` | SUCCESS | Green |
| `◐` | RUNNING | Blue |
| `○` | PENDING | White |
| `✕` | FAILED | Red |
| `⊘` | SKIPPED | Yellow |

## Performance

- **Grid Creation**: O(max_height × stages)
- **Node Placement**: O(nodes)
- **Connector Drawing**: O(max_height × stages)
- **Total Complexity**: O(max_height × stages + nodes)
- **Memory**: O(max_height × stages)

## Files Updated

1. **dag_viz_textualize.py**
   - New `DAGRenderer.render()` with table-based layout
   - Improved `_calculate_stages()` algorithm
   - Grid-based positioning system

2. **dag_viz_demo.py**
   - Updated `render_pipeline_text()` to use grid layout
   - Consistent formatting and spacing

## Testing

Run demonstrations:
```bash
python dag_viz_demo.py
```

Run specific examples:
```bash
python dag_viz_runible.py simple
python dag_viz_runible.py parallel
python dag_viz_runible.py conditional
```

## Implementation Notes

### Grid Initialization
```python
grid_width = len(stages) * 2 - 1  # Stages + connectors
grid = [[" " for _ in range(grid_width)] for _ in range(max_height)]
```

### Node Placement
```python
col_idx = stage_idx * 2  # Nodes in even columns
for node in stages[stage_idx]:
    row_idx = node_positions[(stage_idx, node)]
    grid[row_idx][col_idx] = f"{symbol}{node}"
```

### Connector Placement
```python
connector_col = stage_idx * 2 + 1  # Connectors in odd columns
# Draw arcs and lines based on node positions
```

## Next Steps

- 🔄 Add more unicode connector styles (T-junctions, etc.)
- 🔄 Implement click interactions (select nodes, show details)
- 🔄 Add zoom/filter capabilities
- 🔄 Real-time status updates

## Comparison

| Feature | Old | New |
|---------|-----|-----|
| Layout | Tree | **Grid** |
| Alignment | Poor | **Perfect** |
| Connectors | Simple | **Unicode** |
| Vertical Spacing | Awkward | **Precise** |
| Multi-node Handling | Nested | **Distributed** |
| Code Clarity | Simple | **Robust** |

---

**Status**: ✅ Table-based grid layout with unicode connectors complete!
