import click
from .engine import RunConfig


@click.command(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_FILE")
def runible(file):
    RunConfig(file).get_run().run()
