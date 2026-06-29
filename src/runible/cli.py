import click
from .engine import Run


@click.command(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_FILE")
def runible(file):
    Run(file).run()
