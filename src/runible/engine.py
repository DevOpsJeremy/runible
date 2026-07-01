from __future__ import annotations

import click
import json
import yaml
import jsonschema
import networkx as nx
import queue
from ansible_runner import interface as runner_interface
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from .utilities import as_list


SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


class RunConfig:
    """
    Builds a run configuration instance
    """

    SCHEMA_FILE = SCHEMA_DIR / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    def __init__(self, file):
        self.file = file
        self.config = self.load_config()
        self.clean_config(self.config)
        self.validate_config(self.config)
        self.run = self.get_run()

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

    def get_run(self):
        return Run(self.config)


class StepState(Enum):
    FAILED = auto()
    PENDING = auto()
    RUNNING = auto()
    SKIPPED = auto()
    SUCCESS = auto()
    UNKNOWN = auto()


@dataclass
class StepResult:
    step: str
    status: StepState
    rc: int


class StepConfig:
    def __init__(self, name: str, config: dict, vars: dict = {}):
        self.name = name
        self.config = config
        self.validate_config()
        self.clean_config(self.config)
        self.merge_vars(config, vars)
        self.dependencies = self.get_dependencies()

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

    def get_dependencies(self):
        return self.config.get("after", [])

    def get_step(self, scheduler: Scheduler = None, **kwargs) -> Step:
        return Step(self, scheduler, **kwargs)


class Step:
    STATE_MAP = {
        "starting": StepState.RUNNING,
        "failed": StepState.FAILED,
        "successful": StepState.SUCCESS,
        "running": StepState.RUNNING,
        "unknown": StepState.UNKNOWN,
    }

    def __init__(self, config: StepConfig, scheduler: Scheduler = None, **kwargs):
        self.scheduler = scheduler
        self.config = config
        self.name = self.config.name
        self.playbook = self.config.config.get("run", None)
        self.extravars = self.config.config.get("vars", {})
        self.runner_kwargs = self.get_runner_kwargs(**kwargs)
        self.state = None

    def fail(self, msg: str, source_exception: Exception = None):
        full_msg = f"Error in step '{self.name}': {msg}"
        exception = click.UsageError(full_msg)

        if source_exception is None:
            raise exception
        else:
            raise exception from source_exception

    def clean_playbook(self):
        if self.playbook is None:
            self.fail("The key 'run' was not found")
        try:
            return Path(self.playbook).resolve()
        except Exception as e:
            self.fail(f"Error locating playbook '{self.playbook}'", e)

    def get_runner_kwargs(self, **kwargs):
        runner_kwargs = {
            "playbook": str(self.clean_playbook()),
            "extravars": self.extravars,
        }
        if self.scheduler is not None:
            runner_kwargs = {
                "cancel_callback": self.cancel_callback,
                "finished_callback": self.finished_callback,
                "status_handler": self.status_handler,
                **runner_kwargs,
            }
        return {**kwargs, **runner_kwargs}

    def add_to_graph(self, graph: nx.DiGraph):
        graph.add_node(self.name, step=self)

        for dependency in self.config.dependencies:
            if dependency not in graph:
                raise ValueError(
                    f"Unknown step '{dependency}' referenced by '{self.name}'"
                )

            graph.add_edge(dependency, self.name)

    def cancel_callback(self, *args, **kwargs):
        pass

    def finished_callback(self, *args, **kwargs):
        pass

    def status_handler(self, *args, **kwargs):
        print(f"{args}")
        s = args[0]
        print(s["status"])
        print(self.get_state(s["status"]))
        self.scheduler.queue.put(self)
        pass

    def get_state(self, status: str):
        try:
            return self.STATE_MAP[status]
        except KeyError:
            return StepState.UNKNOWN

    def invoke(self, method: str):
        if method not in ["run", "run_async"]:
            raise click.UsageError(f"Unauthorized method: {method}")

        getattr(runner_interface, method)(**self.runner_kwargs)

    def run(self):
        self.invoke("run")

    def run_async(self):
        self.invoke("run_async")


class Run:
    """
    Assembles a workflow run
    """

    def __init__(self, config: dict, scheduler: Scheduler = None):
        self.config = config
        self.scheduler = scheduler or Scheduler()
        self.steps = self.get_steps()
        self.graph = self.build()

    def get_steps(self):
        return [
            StepConfig(name, config, self.config.get("vars", {})).get_step(
                self.scheduler
            )
            for name, config in self.config.get("steps", {}).items()
        ]

    def build(self):
        graph = nx.DiGraph()

        for step in self.steps:
            step.add_to_graph(graph)

        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Run contains one or more dependency cycles")

        return graph

    def start_scheduler(self):
        if self.scheduler is None:
            return

        self.scheduler.start(self.graph)

    def invoke(self, method: str):
        if method not in ["run", "run_async"]:
            raise click.UsageError(f"Unauthorized method: {method}")

        self.start_scheduler()

        # for step in self.steps:
        # getattr(step, method)()

    def run(self):
        self.invoke("run")

    def run_async(self):
        self.invoke("run_async")


class Executor(ThreadPoolExecutor):
    """
    Executes the workflow
    """

    def __init__(self, run: Run, **kwargs):
        super()
        self.run = run


class Scheduler:
    def __init__(self):
        self.graph = None
        self.queue = None

    def start(self, graph: nx.DiGraph):
        self.graph = graph
        self.queue = queue.Queue()
        self.start_handler()

    def get_starters(self):
        if self.graph is None:
            return

        return [step for step in self.graph.nodes if self.graph.in_degree(step) == 0]

    def start_node(self, node: str):
        if self.graph is None:
            return

        self.graph.nodes[node]["step"].run_async()

    def get_successors(self, node):
        if self.graph is None:
            return

        return self.graph.successors(node)

    def get_handler_thread(self, daemon: bool = True):
        return Thread(target=self.handler, daemon=daemon)

    def start_handler(self):
        thread = self.get_handler_thread()
        thread.start()

    def handler(self):
        print("in handler")
        for node in self.get_starters():
            print(f"processing node '{node}'")
            self.start_node(node)

        while True:
            event = self.queue.get()
            print(f"Working on {event}")
            self.queue.task_done()
