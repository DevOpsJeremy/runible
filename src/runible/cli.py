import click
from .engine_v4 import Run, RunGraph


@click.group(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
def runible():
    pass


@runible.command(name="run")
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_RUN_FILE")
def run(file):
    graph = RunGraph.build_from_file(file)
    Run(graph).run()
