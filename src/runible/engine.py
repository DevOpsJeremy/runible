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
import os

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


class Step:
    def __init__(
        self,
        name: str,
        run: str,
        vars: dict = {},
        after: list = [],
        when: list = [],
        context: Path = Path(os.getcwd()),
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

        self.context = context.resolve()

    def __str__(self):
        return f"<Step {self.name}>"

    @classmethod
    def find_path(cls, path, search_paths):
        for search_path in search_paths:
            find_path = Path(search_path).joinpath(path)
            if find_path.exists():
                return find_path

    def _invoke(self, *args, **kwargs):
        search_paths = [self.context]

        playbook_path = self.find_path(self.run, search_paths)

        ansible_runner.interface.run(playbook=str(playbook_path))

    @classmethod
    def invoke(cls, step: Step, *args, **kwargs):
        step._invoke(*args, **kwargs)


class Plan:
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
        *args,
        **kwargs,
    ):
        self.path = path.resolve()
        print(f"Plan path: {self.path}")
        self.context = self.path.parent
        print(f"Plan context: {self.context}")
        self.vars = vars
        self.steps = self.get_steps(steps)

    def get_steps(self, steps: dict):
        step_set = set()

        for name, step in steps.items():
            if "vars" in step:
                step["vars"] = self.vars | step["vars"]

            step_set.add(Step(name, context=self.context, **step))

        return step_set

    @classmethod
    def from_file(cls, file):
        plan = cls.load_plan(file)
        cls.clean_plan(plan)
        cls.validate_plan(plan)
        return cls(path=Path(file.name), **plan)

    @classmethod
    def load_plan(cls, file):
        return yaml.safe_load(file)

    @classmethod
    def validate_plan(cls, plan):
        try:
            jsonschema.validate(instance=plan, schema=cls.SCHEMA)
            return True
        except jsonschema.exceptions.ValidationError as e:
            path = e.json_path.removeprefix("$.")
            msg = f"{e.message} (at {path})" if path else e.message
            raise click.UsageError(msg) from e

    @classmethod
    def clean_plan(cls, plan):
        return_plan = plan.copy()

        for step_name, step in plan.get("steps", {}).items():
            # Convert strings to list
            for key in ["when", "after"]:
                try:
                    return_plan["steps"][step_name][key] = as_list(step[key])
                except KeyError:
                    pass


class Graph(nx.DiGraph):
    def __init__(self, config: Plan = None):
        super().__init__()
        self.config = config

    @classmethod
    def from_file(cls, file):
        graph = cls(Plan.from_file(file))
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
