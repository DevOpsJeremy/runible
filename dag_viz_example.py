"""
Example: Creating custom DAG visualizations with Textualize

This script demonstrates how to:
1. Create custom DAGs programmatically
2. Set node statuses
3. Visualize them with Textualize
"""

from dag_viz_textualize import DAGApp, NodeStatus, SimpleDAG


def example_ci_cd_pipeline():
    """Example: CI/CD pipeline DAG."""
    dag = SimpleDAG()

    # Define pipeline stages
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

    return dag, statuses, "CI/CD Pipeline"


def example_data_pipeline():
    """Example: Data processing pipeline DAG."""
    dag = SimpleDAG()

    edges = [
        ("Extract", "Validate"),
        ("Validate", "Transform"),
        ("Transform", "Aggregate"),
        ("Transform", "Quality Check"),
        ("Aggregate", "Report"),
        ("Quality Check", "Report"),
        ("Report", "Publish"),
    ]

    for from_node, to_node in edges:
        dag.add_edge(from_node, to_node)

    statuses = {
        "Extract": NodeStatus.SUCCESS,
        "Validate": NodeStatus.SUCCESS,
        "Transform": NodeStatus.RUNNING,
        "Aggregate": NodeStatus.PENDING,
        "Quality Check": NodeStatus.PENDING,
        "Report": NodeStatus.PENDING,
        "Publish": NodeStatus.PENDING,
    }

    return dag, statuses, "Data Pipeline"


def example_multi_branch():
    """Example: Multi-branch workflow DAG."""
    dag = SimpleDAG()

    edges = [
        ("Start", "Feature A"),
        ("Start", "Feature B"),
        ("Start", "Feature C"),
        ("Feature A", "Test A"),
        ("Feature B", "Test B"),
        ("Feature C", "Test C"),
        ("Test A", "Merge"),
        ("Test B", "Merge"),
        ("Test C", "Merge"),
        ("Merge", "Deploy"),
    ]

    for from_node, to_node in edges:
        dag.add_edge(from_node, to_node)

    statuses = {
        "Start": NodeStatus.SUCCESS,
        "Feature A": NodeStatus.SUCCESS,
        "Feature B": NodeStatus.SUCCESS,
        "Feature C": NodeStatus.RUNNING,
        "Test A": NodeStatus.SUCCESS,
        "Test B": NodeStatus.SUCCESS,
        "Test C": NodeStatus.PENDING,
        "Merge": NodeStatus.PENDING,
        "Deploy": NodeStatus.PENDING,
    }

    return dag, statuses, "Multi-Branch Workflow"


def run_example(example_fn):
    """Run a single example."""
    dag, statuses, title = example_fn()

    print(f"\n{'=' * 60}")
    print(f"📊 {title}")
    print(f"{'=' * 60}\n")

    app = DAGApp(dag, statuses)
    app.run()


if __name__ == "__main__":
    # Uncomment the example you want to run
    run_example(example_ci_cd_pipeline)
    # run_example(example_data_pipeline)
    # run_example(example_multi_branch)
