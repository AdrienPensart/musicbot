import logging
import pytest
from musicbot.cli import cli
from musicbot.click_helpers import run_cli

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_completion_show(cli_runner):
    run_cli(cli_runner, cli, ["completion", "show", "zsh"])
