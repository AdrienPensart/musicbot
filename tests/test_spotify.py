import logging
import pytest
from musicbot.cli import cli
from musicbot.click_helpers import run_cli

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_playlists(cli_runner):
    run_cli(cli_runner, cli, ['spotify', 'playlists'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_tracks(cli_runner):
    run_cli(cli_runner, cli, ['spotify', 'tracks'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_diff(cli_runner):
    run_cli(cli_runner, cli, ['spotify', 'tracks'])
