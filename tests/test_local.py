# type: ignore
import json

import pytest
from click_skeleton.testing import run_cli

from musicbot.main import cli


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_query(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'query',
        'select Music;',
        '--dsn', edgedb,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_search(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'search',
        '1995',
        '--dsn', edgedb,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_watch(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'watch',
        '--dsn', edgedb,
        '--timeout', 5,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_artists(cli_runner, edgedb):
    output = run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'artists',
        '--dsn', edgedb,
        '--output', 'json',
    ])
    json.loads(output)


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_soft_clean(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'search',
        '1995',
        '--dsn', edgedb,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_sync(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'sync',
        '--dsn', edgedb,
        '--delete',
        '--yes',
        '/tmp',
        '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_playlist(cli_runner, edgedb):
    output = run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'playlist',
        '--dsn', edgedb,
        '--output', 'json',
    ])
    json.loads(output)


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_bests(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'bests',
        '--dsn', edgedb,
        '/tmp',
        '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_player(cli_runner, edgedb):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'player',
        '--vlc-params', '--vout=dummy --aout=dummy',
        '--dsn', edgedb,
    ])
