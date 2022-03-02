# type: ignore
import logging

import pytest
from click_skeleton.helpers import strip_colors
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.version import __version__

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli(cli_runner):
    run_cli(cli_runner, cli)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_version(cli_runner):
    output1 = strip_colors(run_cli(cli_runner, cli, ['--quiet', '-V']))
    output2 = strip_colors(run_cli(cli_runner, cli, ['--quiet', '--version']))
    output3 = strip_colors(run_cli(cli_runner, cli, ['--quiet', 'version']))
    assert output1 == output2 == output3
    assert __version__ in output1


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_help(cli_runner):
    output1 = strip_colors(run_cli(cli_runner, cli, ['--quiet', '-h']))
    output2 = strip_colors(run_cli(cli_runner, cli, ['--quiet', '--help']))
    output3 = strip_colors(run_cli(cli_runner, cli, ['--quiet', 'help']))
    assert output1 == output2 == output3


@pytest.mark.runner_setup(mix_stderr=False)
def test_config(cli_runner):
    run_cli(cli_runner, cli, ['--quiet', 'config', 'show'])
    run_cli(cli_runner, cli, ['--quiet', 'config', 'print'])
    run_cli(cli_runner, cli, ['--quiet', 'config', 'logging'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_completion_show(cli_runner):
    run_cli(cli_runner, cli, ['--quiet', "completion", "show", "zsh"])
