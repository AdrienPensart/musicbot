import logging
import pytest
from click_skeleton.testing import run_cli
from click_skeleton.helpers import strip_colors

from musicbot.cli import main_cli, __version__

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli(cli_runner):
    run_cli(cli_runner, main_cli)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_version(cli_runner):
    output1 = strip_colors(run_cli(cli_runner, main_cli, ['-V']))
    output2 = strip_colors(run_cli(cli_runner, main_cli, ['--version']))
    output3 = strip_colors(run_cli(cli_runner, main_cli, ['version']))
    assert output1 == output2 == output3
    assert __version__ in output1


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_help(cli_runner):
    output1 = strip_colors(run_cli(cli_runner, main_cli, ['-h']))
    output2 = strip_colors(run_cli(cli_runner, main_cli, ['--help']))
    output3 = strip_colors(run_cli(cli_runner, main_cli, ['help']))
    assert output1 == output2 == output3


@pytest.mark.runner_setup(mix_stderr=False)
def test_config(cli_runner):
    run_cli(cli_runner, main_cli, ['config', 'show'])
    run_cli(cli_runner, main_cli, ['config', 'print'])
    run_cli(cli_runner, main_cli, ['config', 'logging'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_completion_show(cli_runner):
    run_cli(cli_runner, main_cli, ["completion", "show", "zsh"])
