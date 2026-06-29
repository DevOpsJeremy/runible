from click.testing import CliRunner
from .cli import hello


def test_hello():
    runner = CliRunner()
    result = runner.invoke(hello)
    assert result.exit_code == 0
    assert result.output == "Hello world\n"
