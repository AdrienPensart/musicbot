# type: ignore
import json
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
def test_spotify_artist_diff(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'spotify', 'artist-diff',
        '--dsn', edgedb,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_spotify_track_diff(cli_runner, edgedb):
    output = run_cli(cli_runner, cli, [
        '--quiet',
        'spotify', 'track-diff',
        '--dsn', edgedb,
        '--min-threshold', 50,
        '--output', 'json',
    ])
    json.loads(output)
