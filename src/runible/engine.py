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

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


class Step:
    def __init__(
        self,
        name: str,
        run: str,
        vars: dict | None = None,
        after: list | None = None,
        when: list | None = None,
        env: dict | None = None,
        context: Path | None = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.run = run

        if vars is None:
            self.vars = {}
        else:
            self.vars = vars

        if env is None:
            self.env = {}
        else:
            self.env = env

        if after is None:
            self.after = []
        else:
            self.after = as_list(after)

        if when is None:
            self.when = []
        else:
            self.when = as_list(when)

        self.context = context

    def __str__(self):
        return f"<Step {self.name}>"

    def _invoke(self, *args, **kwargs):
        _invoked_kwargs = {"playbook": str(self.run)}

        if self.context is not None:
            _invoked_kwargs["project_dir"] = str(self.context)

        if self.env is not None:
            _invoked_kwargs["envvars"] = self.env

        if self.vars is not None:
            _invoked_kwargs["extravars"] = self.vars

        ansible_runner.interface.run(**_invoked_kwargs)

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
        env: dict | None = None,
        vars: dict | None = None,
        steps: dict | None = None,
        context: Path | None = None,
        *args,
        **kwargs,
    ):
        if vars is None:
            self.vars = {}
        else:
            self.vars = vars

        if env is None:
            self.env = {}
        else:
            self.env = env

        self.context = context
        self.steps = self.get_steps(steps)

    def get_steps(self, steps: dict):
        step_list = []

        if steps is None:
            return step_list

        for name, step in steps.items():
            # Merge plan-level vars with step vars (step overrides plan vars)
            merged_vars = {}
            if self.vars:
                merged_vars.update(self.vars)

            step_vars = step.get("vars")
            if step_vars:
                merged_vars.update(step_vars)

            # Merge plan-level env vars with step env vars (step overrides plan env vars)
            merged_env = {}
            if self.env:
                merged_env.update(self.env)

            step_env = step.get("env")
            if step_env:
                merged_env.update(step_env)

            step_copy = dict(step)
            step_copy["vars"] = merged_vars
            step_copy["env"] = merged_env
            step_list.append(Step(name, context=self.context, **step_copy))

        return step_list

    @classmethod
    def from_file(cls, file):
        plan = cls.load_plan(file)
        cls.validate_plan(plan)
        if plan.get("context", None) is None and getattr(file, "name", None) is not None:
            plan["context"] = Path(file.name).resolve().parent
        plan = cls.clean_plan(plan)
        return cls(**plan)

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

        return return_plan


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
                if dep is None or dep.name not in self:
                    raise ValueError(
                        f"Unknown step '{dep.name}' referenced by '{step.name}'"
                    )

                self.add_edge(dep.name, step.name)

        if not nx.is_directed_acyclic_graph(self):
            raise ValueError("Graph contains one or more dependency cycles")


class Workflow:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def run(
        self,
        fn,
        include_data: bool = True,
        max_workers: int = 5,
        thread_pool_initializer=None,
        thread_pool_initargs=(),
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
                f.result()

                for node in self.graph.successors(completed_node):
                    remaining[node] -= 1

                    if remaining[node] == 0:
                        node_data = self.graph.nodes[node]
                        f = executor.submit(fn, *args, **kwargs, **node_data)
                        future_to_step[f] = node
