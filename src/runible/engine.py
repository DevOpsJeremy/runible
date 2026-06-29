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
        self.load_config()
        self.validate_config(self.config)
        self.workflow = self.build_workflow()

    def load_config(self):
        self.config = yaml.safe_load(self.file)

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
        print(self.workflow.graph.nodes(data=True))
        print([i for i in dir(self.workflow.graph) if not i.startswith("_")])


class Workflow:
    def __init__(self, config: dict):
        self.config = config
        self.graph = self.build()

    def build(self):
        graph = nx.DiGraph()

        for step_name, step in self.config["steps"].items():
            graph.add_node(
                step_name,
                run=step["run"],
                vars=step.get("vars", {}),
                when=step.get("when", []),
            )

        for step_name, step in self.config["steps"].items():
            for dependency in as_list(step.get("after", [])):
                if dependency not in graph:
                    raise ValueError(
                        f"Unknown step '{dependency}' referenced by '{step_name}'"
                    )

                graph.add_edge(dependency, step_name)

        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Run contains one or more dependency cycles")

        return graph
