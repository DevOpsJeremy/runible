import click
from .engine import Run, Graph, run_step


@click.group(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
def runible():
    pass


@runible.command(name="run")
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_RUN_FILE")
def run(file):
    graph = Graph.from_file(file)
    print(graph)
    Run(graph).run(fn=run_step)
