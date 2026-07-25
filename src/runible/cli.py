from __future__ import annotations

import click
from .engine import Workflow, Graph, Step
# TODO remove
from blinker import signal


@click.group(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
def runible():
    pass


@runible.command(name="run")
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_RUN_FILE")
def run(file):
    def print_status(*args, **kargs):
        print(args)
        print(kwargs)

    Workflow(Graph.from_file(file)).run(fn=Step.invoke)
