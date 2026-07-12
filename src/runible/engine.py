from __future__ import annotations

import json
import jsonschema
import networkx as nx
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from runible.utilities import as_list

from datetime import datetime
import time
import random

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"

class Step:
    def __init__(
        self,
        name: str,
        run: str,
        vars: dict = {},
        after: list = [],
        when: list = [],
        *args,
        **kwargs
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
        return f"<Step {self.name}>"


class Config:
    """
    Builds a run configuration instance
    """

    SCHEMA_FILE = SCHEMA_DIR / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    def __init__(
        self,
        vars: dict = {},
        steps: dict = {},
        *args,
        **kwargs
    ):
        self.vars = vars
        self.steps = self.get_steps(steps)

    def get_steps(self, steps: dict):
        step_set = set()

        for name, step in steps.items():
            step_set.add(Step(name, **step))

        return step_set

    @classmethod
    def from_file(cls, file):
        content = cls.load_content(file)
        cls.clean_content(content)
        cls.validate_content(content)
        return cls(**content)


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
    def __init__(self, config: Config = None):
        super().__init__()
        self.config = config

    @classmethod
    def from_file(cls, file):
        graph = cls(Config.from_file(file))
        graph.build()
        return graph

    def build(self):
        if self.config is None or self.config.steps is None:
            raise Exception("No steps found in configuration")

        print([str(s) for s in self.config.steps])

        for step in self.config.steps:
            print(f"adding node: {step}")
            self.add_node(step)

        for step in self.config.steps:
            for dependency in step.after:
                dep = next((d for d in self.config.steps if d.name == dependency), None)
                print(f"step: {step}, adding dependency: {dep}")
                if dep not in self:
                    raise ValueError(
                        f"Unknown step '{dep.name}' referenced by '{step.name}'"
                    )

                self.add_edge(dep, step)

        if not nx.is_directed_acyclic_graph(self):
            raise ValueError("Graph contains one or more dependency cycles")


class Run:
    def __init__(
        self,
        graph: Graph
    ):
        self.graph = graph

    def run(
        self,
        fn,
        max_workers: int = 5,
        thread_pool_initializer = None,
        thread_pool_initargs = None,
        *args, **kwargs
    ):
        remaining = {
            node: self.graph.in_degree(node)
            for node in self.graph.nodes
        }

        completed = set()

        future_to_step = {}

        thread_pool_kwargs = dict(
            max_workers=max_workers,
            initializer=thread_pool_initializer,
            initargs=thread_pool_initargs
        )

        with ThreadPoolExecutor(**thread_pool_kwargs) as executor:
            for node in self.graph.nodes:
                if self.graph.in_degree(node) == 0:
                    f = executor.submit(fn, node, *args, **kwargs)
                    future_to_step[f] = node

            while future_to_step:
                f = next(as_completed(future_to_step))
                node = future_to_step.pop(f)

                for successor in self.graph.successors(node):
                    remaining[successor] -= 1

                    if remaining[successor] == 0:
                        f = executor.submit(fn, successor, *args, **kwargs)
                        future_to_step[f] = successor


# TODO: Delete
def run_step(step):
    wait_time = random.randint(1, 5)

    print(f"{datetime.now()} : START({step})")
    time.sleep(wait_time)
    print(f"{datetime.now()} : END({step})")



