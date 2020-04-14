import json
import pytest
from musicbot.cli import cli
from .conftest import run_cli
from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_sync(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, cli, ['local', 'sync', *common_args, '/tmp', '--dry'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_playlist(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, cli, ['local', 'playlist', *common_args, '--output', 'json'])
    run_cli(cli_runner, cli, ['local', 'playlist', *common_args, '--output', 'table'])
    run_cli(cli_runner, cli, ['local', 'playlist', *common_args, '--output', 'm3u'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_bests(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, cli, ['local', 'bests', *common_args, '/tmp', '--dry'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_stats(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, cli, ['local', 'stats', *common_args])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_player(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, cli, ['local', 'player', *common_args])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_find(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    musics = run_cli(cli_runner, cli, ['local', 'find', *common_args])
    assert len(musics.split("\n")) == 5


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_folders(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    folders_json = run_cli(cli_runner, cli, ['local', 'folders', *common_args, '--output', 'json'])
    folders = json.loads(folders_json)
    assert len(folders) == 2


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_filters(cli_runner, common_args):
    run_cli(cli_runner, cli, ['local', 'load-filters', *common_args])
    filters_json = run_cli(cli_runner, cli, ['local', 'filters', *common_args, '--output', 'json'])
    filters = json.loads(filters_json)
    assert len(filters) == fixtures.filters
    run_cli(cli_runner, cli, ['local', 'filter', *common_args, 'default'])
