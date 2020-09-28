import json
import pytest
from click_skeleton.testing import run_cli
from musicbot.cli import main_cli
from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_query(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, main_cli, [
        'local', 'query',
        *common_args,
        '{doFilterList(minRating: 5.0, artists: ["Buckethead"]){keywords}}',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_count(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    local_count_str = run_cli(cli_runner, main_cli, ['local', 'count', *common_args])
    local_count = int(local_count_str)
    assert local_count == 5


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_sync(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, main_cli, ['local', 'sync', *common_args, '/tmp', '--dry'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_playlist(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, main_cli, ['local', 'playlist', *common_args, '--output', 'json'])
    run_cli(cli_runner, main_cli, ['local', 'playlist', *common_args, '--output', 'table'])
    run_cli(cli_runner, main_cli, ['local', 'playlist', *common_args, '--output', 'm3u'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_bests(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, main_cli, ['local', 'bests', *common_args, '/tmp', '--dry'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_stats(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, main_cli, ['local', 'stats', *common_args])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_player(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    run_cli(cli_runner, main_cli, ['local', 'player', *common_args])


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_folders(cli_runner, common_args, user_musics):  # pylint: disable=unused-argument
    folders_json = run_cli(cli_runner, main_cli, ['local', 'folders', *common_args, '--output', 'json'])
    folders = json.loads(folders_json)
    assert len(folders) == 2


@pytest.mark.runner_setup(mix_stderr=False)
def test_local_filters(cli_runner, common_args):
    run_cli(cli_runner, main_cli, ['local', 'load-filters', *common_args])
    filters_json = run_cli(cli_runner, main_cli, ['local', 'filters', *common_args, '--output', 'json'])
    filters = json.loads(filters_json)
    assert len(filters) == fixtures.filters
    run_cli(cli_runner, main_cli, ['local', 'filter', *common_args, 'default'])
