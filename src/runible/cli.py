from __future__ import annotations

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
    ctx = click.get_current_context()
    Workflow(Graph.from_file(file)).run(fn=Step.invoke, cmdline=" ".join(ctx.args))
