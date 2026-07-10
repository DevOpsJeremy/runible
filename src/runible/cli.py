import click
from .engine_v3 import RunConfig


@click.group(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
def runible():
    pass

@runible.command(name="run")
@click.argument("file", type=click.File("r"), envvar='RUNIBLE_RUN_FILE')
def run(file):
    RunConfig(file).get_run().run()
