import logging

from beartype import beartype
from click.testing import CliRunner
from click_skeleton.helpers import strip_colors
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.version import __version__

logger = logging.getLogger(__name__)


@beartype
def test_cli(cli_runner: CliRunner) -> None:
    _ = run_cli(cli_runner, cli)


@beartype
def test_cli_version(cli_runner: CliRunner) -> None:
    output1 = strip_colors(run_cli(cli_runner, cli, ["--quiet", "-V"]))
    output2 = strip_colors(run_cli(cli_runner, cli, ["--quiet", "--version"]))
    output3 = strip_colors(run_cli(cli_runner, cli, ["--quiet", "version"]))
    assert output1 == output2 == output3
    assert __version__ in output1


@beartype
def test_cli_help(cli_runner: CliRunner) -> None:
    output1 = strip_colors(run_cli(cli_runner, cli, ["--quiet", "-h"]))
    output2 = strip_colors(run_cli(cli_runner, cli, ["--quiet", "--help"]))
    output3 = strip_colors(run_cli(cli_runner, cli, ["--quiet", "help"]))
    assert output1 == output2 == output3
