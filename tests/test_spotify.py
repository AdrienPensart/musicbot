import logging
import pytest
from click_skeleton.testing import run_cli
from musicbot.main import cli

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_cached_token(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'spotify', 'cached-token'
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_playlists(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'spotify', 'playlists'
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_tracks(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'spotify', 'tracks'
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_diff(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'spotify', 'diff',
        *common_args,
    ])
