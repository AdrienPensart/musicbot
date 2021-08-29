import pytest
from click_skeleton.testing import run_cli
from musicbot.main import cli


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_query(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'query',
        *common_args,
        '{doFilterList(minRating: 5.0, artists: ["Buckethead"]){keywords}}',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_count(cli_runner, common_args):
    local_count_str = run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'count',
        *common_args,
    ])
    local_count = int(local_count_str)
    assert local_count == 5


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_sync(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'sync',
        *common_args,
        '/tmp',
        '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_m3u_playlist(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'm3u-playlist',
        *common_args,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_m3u_bests(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'm3u-bests',
        *common_args,
        '/tmp',
        '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_stats(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'stats',
        *common_args,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_player(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'player',
        *common_args,
    ])
