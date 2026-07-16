from __future__ import annotations

import ansible_runner
import click
import json
import jsonschema
import networkx as nx
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from runible.utilities import as_list

# TODO: Delete
from datetime import datetime
import time
import random
import os

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


class StepPlan:
    def __init__(
        self,
        name: str,
        run: str,
        vars: dict = {},
        after: list = [],
        when: list = [],
        *args,
        **kwargs,
    ):
        self.name = name
        self.run = run

        if vars is None:
            self.vars = {}
        else:
            self.vars = vars

        if after is None:
            self.after = []
        else:
            self.after = as_list(after)

        if when is None:
            self.when = []
        else:
            self.when = as_list(when)

    def __str__(self):
        return f"<StepPlan {self.name}>"


class Step:
    def __init__(self):
        pass

    @classmethod
    def run(cls, step: StepPlan):
        print(f"{datetime.now()} : START({step.name})")
        print(f"ansible_runner.interface.run(playbook={step.run})")
        ansible_runner.interface.run(playbook=step.run)
        print(f"{datetime.now()} : END({step.name})")


class RunPlan:
    """
    Builds a run configuration instance
    """

    SCHEMA_FILE = SCHEMA_DIR / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    def __init__(
        self,
        path: Path = Path(os.getcwd()),
        vars: dict = {},
        steps: dict = {},
        *args, **kwargs
    ):
        self.path = path
        self.vars = vars
        self.steps = self.get_steps(steps)

    def get_steps(self, steps: dict):
        step_set = set()

        for name, step in steps.items():
            if "vars" in step:
                step["vars"] = self.vars | step["vars"]

            step_set.add(StepPlan(name, **step))

        return step_set

    @classmethod
    def from_file(cls, file):
        content = cls.load_content(file)
        cls.clean_content(content)
        cls.validate_content(content)
        return cls(
            path=Path(file.name),
            **content
        )

    @classmethod
    def load_content(cls, file):
        return yaml.safe_load(file)

    @classmethod
    def validate_content(cls, content):
        try:
            jsonschema.validate(instance=content, schema=cls.SCHEMA)
            return True
        except jsonschema.exceptions.ValidationError as e:
            path = e.json_path.removeprefix("$.")
            msg = f"{e.message} (at {path})" if path else e.message
            raise click.UsageError(msg) from e

    @classmethod
    def clean_content(cls, content):
        return_content = content.copy()

        for step_name, step in content.get("steps", {}).items():
            # Convert strings to list
            for key in ["when", "after"]:
                try:
                    return_content["steps"][step_name][key] = as_list(step[key])
                except KeyError:
                    pass


class Graph(nx.DiGraph):
    def __init__(self, config: RunPlan = None):
        super().__init__()
        self.config = config

    @classmethod
    def from_file(cls, file):
        graph = cls(RunPlan.from_file(file))
        graph.build()
        return graph

    def build(self):
        if self.config is None or self.config.steps is None:
            raise Exception("No steps found in configuration")

        for step in self.config.steps:
            self.add_node(step.name, step=step)

        for step in self.config.steps:
            for dependency in step.after:
                dep = next((d for d in self.config.steps if d.name == dependency), None)
                if dep.name not in self:
                    raise ValueError(
                        f"Unknown step '{dep.name}' referenced by '{step.name}'"
                    )

                self.add_edge(dep.name, step.name)

        if not nx.is_directed_acyclic_graph(self):
            raise ValueError("Graph contains one or more dependency cycles")


class Workflow:
    def __init__(self, graph: Graph):
        self.graph = graph

    @classmethod
    def from_file(cls, file):
        graph = Graph.from_file(file)
        return cls(graph)

    def run(
        self,
        fn,
        include_data: bool = True,
        max_workers: int = 5,
        thread_pool_initializer=None,
        thread_pool_initargs=None,
        *args,
        **kwargs,
    ):
        remaining = {node: self.graph.in_degree(node) for node in self.graph.nodes}

        future_to_step = {}

        with ThreadPoolExecutor(
            max_workers=max_workers,
            initializer=thread_pool_initializer,
            initargs=thread_pool_initargs,
        ) as executor:
            for node in self.graph.nodes:
                if self.graph.in_degree(node) == 0:
                    node_data = self.graph.nodes[node]
                    f = executor.submit(fn, *args, **kwargs, **node_data)
                    future_to_step[f] = node

            while future_to_step:
                f = next(as_completed(future_to_step))
                completed_node = future_to_step.pop(f)

                for node in self.graph.successors(completed_node):
                    remaining[node] -= 1

                    if remaining[node] == 0:
                        node_data = self.graph.nodes[node]
                        f = executor.submit(fn, *args, **kwargs, **node_data)
                        future_to_step[f] = node
