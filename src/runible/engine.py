from __future__ import annotations

import click
import json
import yaml
import jsonschema
import networkx as nx
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
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
        self.clean_config(self.config)
        self.validate_config(self.config)
        self.workflow = self.build_workflow()

    def load_config(self):
        return yaml.safe_load(self.file)

    @classmethod
    def validate_config(cls, config):
        try:
            jsonschema.validate(instance=config, schema=cls.SCHEMA)
            return True
        except jsonschema.exceptions.ValidationError as e:
            path = e.json_path.removeprefix("$.")
            msg = f"{e.message} (at {path})" if path else e.message
            raise click.UsageError(msg) from e

    @classmethod
    def clean_config(cls, config):
        return_config = config.copy()

        for step_name, step in config.get("steps", {}).items():
            # Convert strings to list
            for key in ["when", "after"]:
                try:
                    return_config["steps"][step_name][key] = as_list(step[key])
                except KeyError:
                    pass

    def build_workflow(self):
        return Workflow(self.config)

    def run(self):
        print(self.config)
        print(self.workflow.graph.nodes(data=True))


class StepState(Enum):
    FAILED = auto()
    PENDING = auto()
    RUNNING = auto()
    SKIPPED = auto()
    SUCCESS = auto()


@dataclass
class StepResult:
    step: str
    status: StepState
    rc: int


# TODO: Add the ansible logic
import random


def run_ansible(step: Step):
    if random.choice([True, False]):
        return 0

    return 1


class Step:
    def __init__(self, name: str, config: dict, vars: dict = {}):
        self.name = name
        self.config = config
        self.validate_config()
        self.merge_vars(config, vars)
        self.clean_config(self.config)
        self.state = None

    @classmethod
    def clean_config(cls, config):
        # Convert strings to list
        for key in ["when", "after"]:
            try:
                config[key] = as_list(config[key])
            except KeyError:
                pass

    @classmethod
    def merge_vars(cls, config: dict, vars: dict):
        config["vars"] = vars | config.get("vars", {})

    def validate_config(self):
        if "run" not in self.config:
            raise click.UsageError(f"The key 'run' was not found for step {self.name}")

    def add_to_graph(self, graph: nx.DiGraph):
        graph.add_node(self.name, step=self)

        for dependency in self.config.get("after", []):
            if dependency not in graph:
                raise ValueError(
                    f"Unknown step '{dependency}' referenced by '{self.name}'"
                )

            graph.add_edge(dependency, self.name)

    def run(self) -> StepResult:
        rc = run_ansible(self)

        return StepResult(
            step=self.name,
            status=StepState.SUCCESS if rc == 0 else StepState.FAILED,
            rc=rc,
        )


class Workflow:
    """
    Builds the workflow graph
    """

    def __init__(self, config: dict):
        self.config = config
        self.steps = self.get_steps()
        self.graph = self.build()

    def get_steps(self):
        return [
            Step(name, config, self.config.get("vars", {}))
            for name, config in self.config.get("steps", {}).items()
        ]

    def build(self):
        graph = nx.DiGraph()

        for step in self.steps:
            step.add_to_graph(graph)

        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Run contains one or more dependency cycles")

        return graph


class Executor(ThreadPoolExecutor):
    """
    Executes the workflow
    """

    def __init__(self, workflow: Workflow, **kwargs):
        super()
        self.workflow = workflow


class Scheduler:
    def __init__(self):
        pass
