import logging
import pytest
from click_skeleton import run_cli  # type: ignore
from click_skeleton.helpers import strip_colors  # type: ignore

from musicbot import __version__
from musicbot.cli import cli

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli(cli_runner):
    run_cli(cli_runner, cli)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_version(cli_runner):
    output1 = strip_colors(run_cli(cli_runner, cli, ['-V']))
    output2 = strip_colors(run_cli(cli_runner, cli, ['--version']))
    output3 = strip_colors(run_cli(cli_runner, cli, ['version']))
    assert output1 == output2 == output3
    assert __version__ in output1


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_help(cli_runner):
    output1 = strip_colors(run_cli(cli_runner, cli, ['-h']))
    output2 = strip_colors(run_cli(cli_runner, cli, ['--help']))
    output3 = strip_colors(run_cli(cli_runner, cli, ['help']))
    assert output1 == output2 == output3


@pytest.mark.runner_setup(mix_stderr=False)
def test_config(cli_runner):
    run_cli(cli_runner, cli, ['config', 'show'])
    run_cli(cli_runner, cli, ['config', 'print'])
    run_cli(cli_runner, cli, ['config', 'logging'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_completion_show(cli_runner):
    run_cli(cli_runner, cli, ["completion", "show", "zsh"])
