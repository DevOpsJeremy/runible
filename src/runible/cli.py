from __future__ import annotations

import shlex

import click

from .engine import Graph, Step, Workflow


@click.group(name="runible", context_settings={"auto_envvar_prefix": "RUNIBLE"})
def runible():
    pass


@runible.command(
    name="run",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_RUN_FILE")
def run(file):
    """CLI command to execute a runible plan from a file.

    ``file`` is an open file object pointing at a YAML plan. Extra CLI args are
    forwarded to the underlying ansible-runner invocation via the ``cmdline``
    parameter.
    """
    ctx = click.get_current_context()
    Workflow(Graph.from_file(file)).run(fn=Step.invoke, cmdline=shlex.join(ctx.args))
