"""
Integration: Using DAG Visualization with Runible

This script demonstrates how to integrate the DAG visualization
with a Runible workflow execution, showing real-time status updates.
"""

from typing import Dict, List
from pathlib import Path
import json

from dag_viz_textualize import SimpleDAG, NodeStatus

try:
    from dag_viz_textualize import DAGApp
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False


def load_runible_workflow(workflow_file: str) -> tuple[SimpleDAG, Dict[str, NodeStatus]]:
    """
    Load a Runible workflow and create a DAG visualization.

    Args:
        workflow_file: Path to runible.yml or similar workflow file

    Returns:
        (DAG, statuses) tuple
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML required. Install with: python -m pip install pyyaml")

    dag = SimpleDAG()
    statuses = {}

    # Load the workflow
    with open(workflow_file) as f:
        workflow = yaml.safe_load(f)

    # Process workflow tasks
    if "tasks" in workflow:
        tasks = workflow["tasks"]

        for task in tasks:
            task_name = task.get("name", "Unknown")
            statuses[task_name] = NodeStatus.PENDING

            # Check for dependencies
            depends_on = task.get("depends_on", [])
            if isinstance(depends_on, str):
                depends_on = [depends_on]

            for dependency in depends_on:
                dag.add_edge(dependency, task_name)

            # Check for a condition (if not met, mark as skipped)
            if "when" in task and not task["when"]:
                statuses[task_name] = NodeStatus.SKIPPED

    return dag, statuses


def create_workflow_dag_from_dict(workflow_dict: dict) -> tuple[SimpleDAG, Dict[str, NodeStatus]]:
    """
    Create a DAG from a workflow dictionary structure.

    Example workflow structure:
    {
        "name": "Deploy Pipeline",
        "tasks": [
            {"name": "Checkout", "depends_on": []},
            {"name": "Build", "depends_on": ["Checkout"]},
            {"name": "Test", "depends_on": ["Build"]},
            {"name": "Deploy", "depends_on": ["Test"]},
        ]
    }
    """
    dag = SimpleDAG()
    statuses = {}

    for task in workflow_dict.get("tasks", []):
        task_name = task["name"]
        statuses[task_name] = NodeStatus.PENDING

        for dependency in task.get("depends_on", []):
            dag.add_edge(dependency, task_name)

    return dag, statuses


def create_ansible_playbook_dag(playbook_file: str) -> tuple[SimpleDAG, Dict[str, NodeStatus]]:
    """
    Create a DAG from an Ansible playbook structure.

    This extracts play and task relationships.
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML required. Install with: python -m pip install pyyaml")

    dag = SimpleDAG()
    statuses = {}
    previous_task = None

    with open(playbook_file) as f:
        playbooks = yaml.safe_load(f)

    for play in playbooks:
        play_name = play.get("name", "Play")
        statuses[play_name] = NodeStatus.PENDING

        if previous_task:
            dag.add_edge(previous_task, play_name)

        previous_task = play_name

        # Extract tasks from the play
        for task in play.get("tasks", []):
            task_name = task.get("name", "Task")
            statuses[task_name] = NodeStatus.PENDING

            if previous_task and task_name != play_name:
                dag.add_edge(previous_task, task_name)
                previous_task = task_name

    return dag, statuses


def example_simple_deployment_dag() -> tuple[SimpleDAG, Dict[str, NodeStatus]]:
    """Example: Simple deployment workflow."""
    workflow = {
        "name": "Deployment Pipeline",
        "tasks": [
            {"name": "Checkout Source", "depends_on": []},
            {"name": "Validate Code", "depends_on": ["Checkout Source"]},
            {"name": "Build Artifacts", "depends_on": ["Validate Code"]},
            {"name": "Run Unit Tests", "depends_on": ["Build Artifacts"]},
            {"name": "Run Integration Tests", "depends_on": ["Run Unit Tests"]},
            {"name": "Build Docker Image", "depends_on": ["Run Integration Tests"]},
            {"name": "Push to Registry", "depends_on": ["Build Docker Image"]},
            {"name": "Deploy to Staging", "depends_on": ["Push to Registry"]},
            {"name": "Smoke Tests", "depends_on": ["Deploy to Staging"]},
            {"name": "Deploy to Production", "depends_on": ["Smoke Tests"]},
        ]
    }

    dag, statuses = create_workflow_dag_from_dict(workflow)

    # Simulate some progress
    statuses["Checkout Source"] = NodeStatus.SUCCESS
    statuses["Validate Code"] = NodeStatus.SUCCESS
    statuses["Build Artifacts"] = NodeStatus.SUCCESS
    statuses["Run Unit Tests"] = NodeStatus.RUNNING

    return dag, statuses


def example_parallel_tasks_dag() -> tuple[SimpleDAG, Dict[str, NodeStatus]]:
    """Example: Workflow with parallel execution."""
    workflow = {
        "name": "Parallel Testing",
        "tasks": [
            {"name": "Setup", "depends_on": []},
            {"name": "Backend Tests", "depends_on": ["Setup"]},
            {"name": "Frontend Tests", "depends_on": ["Setup"]},
            {"name": "E2E Tests", "depends_on": ["Setup"]},
            {"name": "Security Scan", "depends_on": ["Setup"]},
            {"name": "Merge Results", "depends_on": [
                "Backend Tests", "Frontend Tests", "E2E Tests", "Security Scan"
            ]},
            {"name": "Deploy", "depends_on": ["Merge Results"]},
        ]
    }

    dag, statuses = create_workflow_dag_from_dict(workflow)

    # Simulate parallel execution
    statuses["Setup"] = NodeStatus.SUCCESS
    statuses["Backend Tests"] = NodeStatus.SUCCESS
    statuses["Frontend Tests"] = NodeStatus.RUNNING
    statuses["E2E Tests"] = NodeStatus.RUNNING
    statuses["Security Scan"] = NodeStatus.PENDING

    return dag, statuses


def example_with_conditionals_dag() -> tuple[SimpleDAG, Dict[str, NodeStatus]]:
    """Example: Workflow with conditional tasks."""
    dag = SimpleDAG()
    statuses = {
        "Start": NodeStatus.SUCCESS,
        "Check Version": NodeStatus.SUCCESS,
        "Patch Release": NodeStatus.SKIPPED,
        "Minor Release": NodeStatus.RUNNING,
        "Major Release": NodeStatus.PENDING,
        "Update Changelog": NodeStatus.PENDING,
        "Publish": NodeStatus.PENDING,
    }

    # Main flow
    dag.add_edge("Start", "Check Version")
    dag.add_edge("Check Version", "Patch Release")
    dag.add_edge("Check Version", "Minor Release")
    dag.add_edge("Check Version", "Major Release")
    dag.add_edge("Patch Release", "Update Changelog")
    dag.add_edge("Minor Release", "Update Changelog")
    dag.add_edge("Major Release", "Update Changelog")
    dag.add_edge("Update Changelog", "Publish")

    return dag, statuses


if __name__ == "__main__":
    import sys

    examples = {
        "simple": example_simple_deployment_dag,
        "parallel": example_parallel_tasks_dag,
        "conditional": example_with_conditionals_dag,
    }

    # Choose example
    example_name = sys.argv[1] if len(sys.argv) > 1 else "simple"

    if example_name not in examples:
        print(f"Available examples: {', '.join(examples.keys())}")
        sys.exit(1)

    dag, statuses = examples[example_name]()

    print(f"\n🚀 Running: {example_name} example")
    print("=" * 60)

    if HAS_TEXTUAL:
        try:
            app = DAGApp(dag, statuses)
            app.run()
        except Exception as e:
            print(f"Error: {e}")
            print("Falling back to text mode...")
    else:
        print("Textual not available. Displaying text mode output:\n")

    # Text mode fallback
    for node in dag.get_all_nodes():
        status = statuses.get(node, NodeStatus.PENDING)
        print(f"  {node}: {status.value}")
