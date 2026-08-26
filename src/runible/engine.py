from __future__ import annotations

import json
import shlex
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.metadata import entry_points
from pathlib import Path
from threading import Thread

import ansible_runner
import click
import jsonschema
import networkx as nx
import yaml
from blinker import signal

from .utilities import as_list

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


class Step:
    """Represents a single step in a plan.

    A ``Step`` wraps a playbook invocation and associated metadata.

    Public attributes
    - ``name``: logical name of the step
    - ``run``: playbook path (or command) to execute
    - ``plan``: parent ``Plan`` instance
    - ``env``: dict of environment variables passed to the invocation
    - ``vars``: dict of extra variables passed to Ansible
    - ``tags``: list of tags included for this step
    - ``skip_tags``: list of tags to skip for this step
    - ``after``: list of step names this step depends on
    - ``when``: list of condition expressions

    Important methods
    - ``_invoke``: perform the actual ansible invocation (internal)
    - ``invoke``: class-level wrapper that calls ``_invoke``
    - Signal helpers such as ``start``, ``event_handler``, ``finished_callback``
      emit lifecycle events via blinker signals.
    """

    def __init__(
        self,
        name: str,
        run: str,
        plan: Plan,
        env: dict | None = None,
        vars: dict | None = None,
        tags: list | str | None = None,
        skip_tags: list | str | None = None,
        after: list | None = None,
        when: list | None = None,
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

        if tags is None:
            self.tags = []
        else:
            self.tags = as_list(tags)

        if skip_tags is None:
            self.skip_tags = []
        else:
            self.skip_tags = as_list(skip_tags)

        if after is None:
            self.after = []
        else:
            self.after = as_list(after)

        if when is None:
            self.when = []
        else:
            self.when = as_list(when)

        self.plan = plan

    def __str__(self):
        return f"<Step {self.name}>"

    def get_context(self):
        """Get the context (working directory) from the plan"""
        return self.plan.context

    def get_interface(self):
        """Get the interface from the plan"""
        return self.plan.interface

    def start(self):
        """Emit the ``start`` lifecycle signal for this step."""
        self.signal("start")

    def event_handler(self, event_data):
        """Handle an event from ansible-runner and re-emit it as an ``event`` signal.

        ``event_data`` is a dict payload forwarded to listeners.
        """
        self.signal("event", **event_data)

    def cancel_callback(self):
        """Emit a ``cancel`` signal to notify listeners the step was cancelled."""
        self.signal("cancel")

    def finished_callback(self, runner: ansible_runner.runner.Runner):
        """Called when ansible-runner completes; emits a ``finished`` signal
        including the ``runner`` instance."""
        self.signal("finished", runner=runner)

    def status_handler(
        self,
        status_data: dict,
        runner_config: ansible_runner.runner_config.RunnerConfig,
    ):
        """Receive status updates from ansible-runner and forward them as a
        ``status`` signal to listeners.
        """
        self.signal("status", status_data=status_data, runner_config=runner_config)

    def artifacts_handler(self, artifact_dir: str):
        """Notify listeners with the artifacts directory for a completed run."""
        self.signal("artifacts", artifact_dir=artifact_dir)

    def end(self):
        """Emit the ``end`` lifecycle signal for this step."""
        self.signal("end")

    def _invoke(
        self, cmdline: str | None = None, run_async: bool = False, *args, **kwargs
    ) -> ansible_runner.runner.Runner | tuple[Thread, ansible_runner.runner.Runner]:
        invoke_kwargs = {
            "playbook": str(self.run),
            "event_handler": self.event_handler,
            "cancel_callback": self.cancel_callback,
            "finished_callback": self.finished_callback,
            "status_handler": self.status_handler,
            "artifacts_handler": self.artifacts_handler,
        }

        context = self.get_context()
        if context is not None:
            invoke_kwargs["project_dir"] = str(context)

        if self.env is not None:
            invoke_kwargs["envvars"] = self.env

        if self.vars is not None:
            invoke_kwargs["extravars"] = self.vars

        if cmdline is not None:
            invoke_kwargs["cmdline"] = cmdline

        if self.tags is not None and len(self.tags) > 0:
            tags = f"--tags {shlex.quote(','.join(self.tags))}"
            cmdline = invoke_kwargs.get("cmdline", "")
            invoke_kwargs["cmdline"] = f"{cmdline} {tags}".strip()

        if self.skip_tags is not None and len(self.skip_tags) > 0:
            skip_tags = f"--skip-tags {shlex.quote(','.join(self.skip_tags))}"
            cmdline = invoke_kwargs.get("cmdline", "")
            invoke_kwargs["cmdline"] = f"{cmdline} {skip_tags}".strip()

        invoke_kwargs["quiet"] = self.get_interface().quiet

        if run_async:
            return ansible_runner.interface.run_async(**invoke_kwargs)

        self.start()
        try:
            return ansible_runner.interface.run(**invoke_kwargs)
        finally:
            self.end()

    @classmethod
    def invoke(cls, step: Step, *args, **kwargs):
        """Class-level entrypoint used by the workflow runner to invoke a step.

        This method delegates to the instance ``_invoke`` implementation.
        """
        step._invoke(*args, **kwargs)

    def signal(self, status: str, **kwargs):
        """Send a blinker signal named ``status`` with any additional kwargs."""
        signal(status).send(self, **kwargs)


class Plan:
    """Builds a run configuration instance from YAML data.

    A ``Plan`` encapsulates top-level configuration such as global
    ``env``, ``vars``, ``tags`` and ``skip_tags`` and produces a list of
    ``Step`` objects via ``get_steps``.

    Use ``from_file`` or ``load_plan`` to construct a Plan from a
    YAML file. ``validate_plan`` enforces the JSON schema defined in
    ``schemas/run.schema.json``.
    """

    SCHEMA_FILE = SCHEMA_DIR / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    entry_group = "runible"

    def __init__(
        self,
        env: dict | None = None,
        vars: dict | None = None,
        tags: list | str | None = None,
        skip_tags: list | str | None = None,
        steps: dict | None = None,
        interface: str = "default",
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

        if tags is None:
            self.tags = []
        else:
            self.tags = as_list(tags)

        if skip_tags is None:
            self.skip_tags = []
        else:
            self.skip_tags = as_list(skip_tags)

        interface_class = self.get_interface_object(interface)
        self.interface = interface_class()
        self.context = context
        self.steps = self.get_steps(steps)

    def get_interface_object(self, name: str):
        """Locate and load an interface plugin by entry-point name.

        Searches the ``entry_group`` for plugins named ``name`` and returns the
        loaded class. Raises a ``click.UsageError`` if no plugin (or more
        than one without a clear preference) is found, or if loading fails.
        """
        eps = entry_points()
        if hasattr(eps, "select"):
            interface_plugins = [
                i for i in eps.select(group=self.entry_group) if i.name == name
            ]
        else:
            interface_plugins = [
                i for i in eps.get(self.entry_group, []) if i.name == name
            ]
        if len(interface_plugins) == 0:
            raise click.UsageError(
                f"The '{name}' interface plugin was not found in entry-point group '{self.entry_group}'. "
                "Make sure the plugin is installed so entry points are registered."
            )

        interface_plugin = interface_plugins[0]

        if len(interface_plugins) > 1:
            preferred_plugins = [
                i
                for i in interface_plugins
                if getattr(i, "dist", None) is not None and i.dist.name == __package__
            ]
            if preferred_plugins:
                interface_plugin = preferred_plugins[0]
            else:
                raise click.UsageError(
                    f"Multiple {self.entry_group} plugins named '{name}' were found; please uninstall the extra plugin(s)"
                )
        try:
            return interface_plugin.load()
        except Exception as e:
            raise click.UsageError(
                f"Failed to load interface plugin '{name}' from '{getattr(interface_plugin, 'value', '<unknown>')}'"
            ) from e

    def get_steps(self, steps: dict):
        """Turn the raw steps mapping from the plan into a list of ``Step``.

        This merges plan-level ``vars``, ``env``, ``tags`` and ``skip_tags``
        into each step's configuration so that step-level values override or
        extend plan-level values.
        """
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

            # Merge plan-level tags with step tags (plan tags are combined with step tags)
            merged_tags = []
            if self.tags:
                merged_tags = [*self.tags]

            step_tags = step.get("tags", None)
            if step_tags is not None:
                merged_tags = [*merged_tags, *as_list(step_tags)]

            # Merge plan-level skip_tags with step skip_tags (plan skip_tags are combined with step skip_tags)
            merged_skip_tags = []
            if self.skip_tags:
                merged_skip_tags = [*self.skip_tags]

            step_skip_tags = step.get("skip_tags", None)
            if step_skip_tags is not None:
                merged_skip_tags = [*merged_skip_tags, *as_list(step_skip_tags)]

            step_copy = dict(step)
            step_copy["vars"] = merged_vars
            step_copy["env"] = merged_env
            step_copy["tags"] = merged_tags
            step_copy["skip_tags"] = merged_skip_tags
            step_list.append(Step(name, plan=self, **step_copy))

        return step_list

    @classmethod
    def from_file(cls, file):
        """Load, validate, and normalize a plan from an open file object.

        Returns an initialized ``Plan`` instance. The plan's ``context`` is
        set to the file's directory if not explicitly provided in the YAML.
        """
        plan = cls.load_plan(file)
        cls.validate_plan(plan)
        if (
            plan.get("context", None) is None
            and getattr(file, "name", None) is not None
        ):
            plan["context"] = Path(file.name).resolve().parent
        plan = cls.clean_plan(plan)
        return cls(**plan)

    @classmethod
    def load_plan(cls, file):
        """Parse YAML from ``file`` and return the resulting mapping."""
        return yaml.safe_load(file)

    @classmethod
    def validate_plan(cls, plan):
        """Validate the plan mapping against the JSON schema.

        Raises a ``click.UsageError`` on validation errors with a helpful
        message indicating the failing path.
        """
        try:
            jsonschema.validate(instance=plan, schema=cls.SCHEMA)
            return True
        except jsonschema.exceptions.ValidationError as e:
            path = e.json_path.removeprefix("$.")
            msg = f"{e.message} (at {path})" if path else e.message
            raise click.UsageError(msg) from e

    @classmethod
    def clean_plan(cls, plan):
        """Normalize plan fields.

        Converts string-valued ``when`` and ``after`` entries into lists so
        downstream code can always treat them uniformly as sequences.
        """
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
    """Directed graph of steps built from a ``Plan``.

    Nodes are step names and node data includes the ``Step`` object under
    the ``'step'`` key. Construct via ``from_file`` which reads a plan and
    populates the graph. ``build`` validates dependencies and detects
    cycles.
    """

    def __init__(self, config: Plan = None):
        super().__init__()
        self.config = config

    @classmethod
    def from_file(cls, file):
        """Create a Graph from a plan file and build its dependencies."""
        graph = cls(Plan.from_file(file))
        graph.build()
        return graph

    def build(self):
        """Populate nodes and edges from the configured ``Plan``.

        Validates that every declared dependency exists and that the graph has
        no cycles; raises on error.
        """
        if self.config is None or not self.config.steps:
            raise click.UsageError("No steps found in configuration")

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
    """Executor for a step graph that runs ready nodes in a thread pool.

    The ``run`` method schedules steps whose dependencies are satisfied and
    executes the provided callable for each node. The callable receives node
    data (including the ``step`` object) as keyword arguments.
    """

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
        """Execute the workflow.

        ``fn`` is the callable invoked for each ready node. It receives the node
        data (including the ``step`` object) as keyword arguments. The method
        schedules work on a thread pool with up to ``max_workers`` threads and
        respects dependencies defined in the graph.
        """
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
