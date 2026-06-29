import click
import json
import yaml
import jsonschema
from pathlib import Path


class Run:
    """
    Builds a run instance
    """

    SCHEMA_FILE = Path(__file__).resolve().parent / "schemas" / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    def __init__(self, file):
        self.file = file
        self.load_config()
        self.validate_config()

    def load_config(self):
        self.config = yaml.safe_load(self.file)

    def validate_config(self):
        try:
            jsonschema.validate(instance=self.config, schema=Run.SCHEMA)
        except jsonschema.exceptions.ValidationError as E:
            raise click.UsageError(E.message)

    def run(self):
        print(self.config)
