from __future__ import annotations

import click
from .engine import Workflow, Step


@click.group(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
def runible():
    pass


@runible.command(name="run")
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_RUN_FILE")
def run(file):
    Workflow.from_file(file).run(fn=Step.run)
