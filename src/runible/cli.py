from __future__ import annotations

import click

from .engine import Graph, Step, Workflow


@click.group(name="runible", context_settings={"auto_envvar_prefix": "RUNIBLE"})
def runible():
    pass


@runible.command(name="run")
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_RUN_FILE")
def run(file):
    Workflow(Graph.from_file(file)).run(fn=Step.invoke)
