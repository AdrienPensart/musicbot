# type: ignore
import json

import pytest
from click_skeleton.testing import run_cli

from musicbot.main import cli


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_query(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'query',
        'select Music;',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_sync(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'sync',
        '/tmp',
        '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_playlist(cli_runner):
    output = run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'playlist',
        '--output', 'json',
    ])
    json.loads(output)


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_bests(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'bests',
        '/tmp',
        '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_player(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'player',
    ])
