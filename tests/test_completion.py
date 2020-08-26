import logging
import pytest
from click_skeleton import run_cli
from musicbot.cli import cli

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_completion_show(cli_runner):
    run_cli(cli_runner, cli, ["completion", "show", "zsh"])
