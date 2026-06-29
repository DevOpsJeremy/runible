import click
import json
from pathlib import Path
from yaml import safe_load
from jsonschema import validate
from jsonschema.exceptions import ValidationError


@click.group(name="runible", context_settings=dict(auto_envvar_prefix="RUNIBLE"))
def runible():
    pass


@runible.command(name="run")
@click.argument("file", type=click.File("r"), envvar="RUNIBLE_RUN_FILE")
def run(file):
    Run(file).run()


class Run:
    """
    Builds a run instance
    """

    SCHEMA_FILE = Path(__file__).resolve().parent / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    def __init__(self, file):
        self.file = file
        self.load_config()
        self.validate_config()

    def load_config(self):
        self.config = safe_load(self.file)

    def validate_config(self):
        try:
            validate(instance=self.config, schema=Run.SCHEMA)
        except ValidationError as E:
            raise click.UsageError([i for i in dir(E) if not i.startswith("_")])

    def run(self):
        print(self.config)
