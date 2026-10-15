#!/usr/bin/env python
"""
Demonstration of horizontal CI/CD pipeline visualization.
Shows left-to-right layout with proper vertical distribution.
"""

from dag_viz_textualize import SimpleDAG, NodeStatus, STATUS_SYMBOLS


def demo_simple_linear():
    """Simple linear pipeline."""
    dag = SimpleDAG()
    edges = [
        ("Checkout", "Build"),
        ("Build", "Test"),
        ("Test", "Deploy"),
    ]
    for f, t in edges:
        dag.add_edge(f, t)
    
    statuses = {
        "Checkout": NodeStatus.SUCCESS,
        "Build": NodeStatus.SUCCESS,
        "Test": NodeStatus.RUNNING,
        "Deploy": NodeStatus.PENDING,
    }
    return dag, statuses


def demo_parallel_tests():
    """Parallel execution at one stage."""
    dag = SimpleDAG()
    edges = [
        ("Setup", "UnitTests"),
        ("Setup", "IntegrationTests"),
        ("Setup", "E2ETests"),
        ("UnitTests", "Report"),
        ("IntegrationTests", "Report"),
        ("E2ETests", "Report"),
        ("Report", "Deploy"),
    ]
    for f, t in edges:
        dag.add_edge(f, t)
    
    statuses = {
        "Setup": NodeStatus.SUCCESS,
        "UnitTests": NodeStatus.SUCCESS,
        "IntegrationTests": NodeStatus.RUNNING,
        "E2ETests": NodeStatus.RUNNING,
        "Report": NodeStatus.PENDING,
        "Deploy": NodeStatus.PENDING,
    }
    return dag, statuses


def demo_complex_flow():
    """More complex workflow."""
    dag = SimpleDAG()
    edges = [
        ("Source", "Lint"),
        ("Source", "Build"),
        ("Lint", "Test"),
        ("Build", "Test"),
        ("Test", "Staging"),
        ("Test", "Docs"),
        ("Staging", "Smoke"),
        ("Docs", "Publish"),
        ("Smoke", "Production"),
        ("Publish", "Production"),
    ]
    for f, t in edges:
        dag.add_edge(f, t)
    
    statuses = {
        "Source": NodeStatus.SUCCESS,
        "Lint": NodeStatus.SUCCESS,
        "Build": NodeStatus.SUCCESS,
        "Test": NodeStatus.SUCCESS,
        "Staging": NodeStatus.RUNNING,
        "Docs": NodeStatus.RUNNING,
        "Smoke": NodeStatus.PENDING,
        "Publish": NodeStatus.PENDING,
        "Production": NodeStatus.PENDING,
    }
    return dag, statuses


def render_pipeline_text(dag, statuses):
    """Render pipeline as text with table-based layout (for environments without Textual)."""
    # Calculate stages
    stages = {}
    node_levels = {}
    
    def get_level(node):
        if node in node_levels:
            return node_levels[node]
        deps = dag.nodes[node].dependencies
        if not deps:
            level = 0
        else:
            level = max(get_level(dep) for dep in deps) + 1
        node_levels[node] = level
        return level
    
    for node in dag.get_all_nodes():
        level = get_level(node)
        if level not in stages:
            stages[level] = []
        stages[level].append(node)
    
    for level in stages:
        stages[level].sort()
    
    max_height = max(len(nodes) for nodes in stages.values()) if stages else 1
    node_positions = {}  # (stage_idx, node_name) -> row_idx
    
    # Calculate positions
    for stage_idx in sorted(stages.keys()):
        nodes_in_stage = stages[stage_idx]
        num_nodes = len(nodes_in_stage)
        
        if num_nodes == 1:
            row_idx = max_height // 2
            node_positions[(stage_idx, nodes_in_stage[0])] = row_idx
        else:
            total_space = max_height - 1 if max_height > 1 else 1
            for i, node in enumerate(nodes_in_stage):
                row_idx = round(i * total_space / (num_nodes - 1)) if num_nodes > 1 else 0
                node_positions[(stage_idx, node)] = row_idx
    
    # Build grid
    grid_width = len(stages) * 2 - 1
    grid = [[" " for _ in range(grid_width)] for _ in range(max_height)]
    
    # Place nodes
    for stage_idx in sorted(stages.keys()):
        col_idx = stage_idx * 2
        for node in stages[stage_idx]:
            row_idx = node_positions[(stage_idx, node)]
            status = statuses.get(node, NodeStatus.PENDING)
            symbol = STATUS_SYMBOLS[status]
            grid[row_idx][col_idx] = f"{symbol}{node}"
    
    # Draw connectors
    for stage_idx in sorted(stages.keys())[:-1]:
        connector_col = stage_idx * 2 + 1
        current_nodes = stages[stage_idx]
        next_nodes = stages[stage_idx + 1]
        
        current_rows = sorted([node_positions[(stage_idx, n)] for n in current_nodes])
        next_rows = sorted([node_positions[(stage_idx + 1, n)] for n in next_nodes])
        
        min_curr = min(current_rows)
        max_curr = max(current_rows)
        min_next = min(next_rows)
        max_next = max(next_rows)
        
        for row_idx in range(max_height):
            if row_idx in current_rows and row_idx in next_rows:
                # Straight line
                grid[row_idx][connector_col] = "─"
            elif row_idx in current_rows:
                # Arc from current node
                if row_idx < min_next:
                    grid[row_idx][connector_col] = "╭"
                else:
                    grid[row_idx][connector_col] = "╰"
            elif row_idx in next_rows:
                # Arc to next node
                if row_idx < min_curr:
                    grid[row_idx][connector_col] = "╭"
                else:
                    grid[row_idx][connector_col] = "╰"
            elif min_curr <= row_idx <= max_curr or min_next <= row_idx <= max_next:
                # Vertical connector line between arcs
                grid[row_idx][connector_col] = "│"
    
    # Convert grid to string with proper spacing
    lines = []
    for row in grid:
        # Process each cell with proper formatting
        line_parts = []
        for i, cell in enumerate(row):
            if len(cell) > 1:  # It's a node
                # Pad node name for alignment
                line_parts.append(f"{cell:<24}")
            else:  # It's a connector
                # Center single character connectors in fixed width
                line_parts.append(f"{cell:^24}")
        lines.append("".join(line_parts))
    
    return "\n".join(lines)


if __name__ == "__main__":
    demos = [
        ("Simple Linear Pipeline", demo_simple_linear),
        ("Parallel Tests Stage", demo_parallel_tests),
        ("Complex Multi-Branch Flow", demo_complex_flow),
    ]
    
    print("\n" + "="*100)
    print("HORIZONTAL CI/CD PIPELINE VISUALIZATION")
    print("="*100)
    
    for title, demo_fn in demos:
        dag, statuses = demo_fn()
        print(f"\n📊 {title}")
        print("-" * 100)
        print(render_pipeline_text(dag, statuses))
    
    print("\n" + "="*100)
    print("Symbol Reference:")
    print("  ● SUCCESS    ◐ RUNNING    ○ PENDING    ✕ FAILED    ⊘ SKIPPED")
    print("\nLayout Rules:")
    print("  • Single items at a stage are centered vertically")
    print("  • Multiple items at a stage are evenly distributed")
    print("  • Arrows (→) connect stages from left to right")
    print("="*100 + "\n")
