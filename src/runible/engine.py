import click
import json
import yaml
import jsonschema
from pathlib import Path
import networkx as nx
from .utilities import as_list


class Run:
    """
    Builds a run instance
    """

    SCHEMA_FILE = Path(__file__).resolve().parent / "schemas" / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    def __init__(self, file):
        self.file = file
        self.config = self.load_config()
        self.validate_config(self.config)
        self.workflow = self.build_workflow()

    def load_config(self):
        return yaml.safe_load(self.file)

    @classmethod
    def validate_config(cls, config):
        try:
            jsonschema.validate(instance=config, schema=cls.SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            path = e.json_path.removeprefix("$.")
            msg = f"{e.message} (at {path})" if path else e.message
            raise click.UsageError(msg) from e

    def build_workflow(self):
        return Workflow(self.config)

    def run(self):
        print(self.config)
        print(self.workflow.graph.nodes(data=True))


class Workflow:
    def __init__(self, config: dict):
        self.config = config
        self.graph = self.build()

    def add_step(self, name: str, step_config: dict, graph: nx.DiGraph):
        step_vars = step_config.get("vars", {})
        combined_vars = self.config.get("vars", {}) | step_vars

        if "run" not in step_config:
            raise click.UsageError(f"The key 'run' was not found for step {name}")

        step_kwargs = {
            "run": step_config["run"],
            "vars": combined_vars,
            "when": as_list(step_config.get("when", [])),
        }

        graph.add_node(name, **step_kwargs)

        for dependency in as_list(step_config.get("after", [])):
            if dependency not in graph:
                raise ValueError(f"Unknown step '{dependency}' referenced by '{name}'")

            graph.add_edge(dependency, name)

    def build(self):
        graph = nx.DiGraph()

        for step_name, step in self.config.get("steps", {}).items():
            self.add_step(step_name, step, graph)

        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Run contains one or more dependency cycles")

        return graph
