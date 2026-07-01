import pytest
import click
from .engine import RunConfig

VALID_CONFIG = {
    "vars": {"var1": "val1"},
    "steps": {
        "step1": {"run": "playbook1.yml", "vars": {"var2": "val2"}},
        "step2": {"run": "playbook2.yml", "after": ["step1"]},
        "step3": {
            "run": "playbook3.yml",
            "after": ["step1"],
            "when": "step1 is failed",
        },
        "step4": {"run": "playbook4.yml", "after": ["step2", "step3"]},
    },
}

INVALID_CONFIG = {"other_key": "other_value"}


def test_valid_configuration():
    RunConfig.validate_config(VALID_CONFIG)


def test_invalid_configuration():
    with pytest.raises(click.UsageError):
        RunConfig.validate_config(INVALID_CONFIG)
