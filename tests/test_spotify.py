import logging
import pytest
from click_skeleton.testing import run_cli
from musicbot.cli import main_cli

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_playlists(cli_runner):
    run_cli(cli_runner, main_cli, [
        'spotify', 'playlists'
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_tracks(cli_runner):
    run_cli(cli_runner, main_cli, [
        'spotify', 'tracks'
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_diff(cli_runner, common_args):
    run_cli(cli_runner, main_cli, [
        'spotify', 'diff',
        *common_args,
    ])
