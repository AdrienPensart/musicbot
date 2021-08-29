import json
import pytest
from click_skeleton.testing import run_cli
from musicbot.main import cli
from musicbot.music.music_filter import default_filters


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_show(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'filter', 'show',
        *common_args,
        'default',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_delete(cli_runner, common_args):
    run_cli(cli_runner, cli, [
        '--quiet',
        'filter', 'delete',
        *common_args,
        'default',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_count(cli_runner, common_args):
    count_filters_str = run_cli(cli_runner, cli, [
        '--quiet',
        'filter', 'count',
        *common_args,
    ])
    count_filters = int(count_filters_str)
    assert count_filters == len(default_filters)


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_list(cli_runner, common_args):
    filters_json = run_cli(cli_runner, cli, [
        '--quiet',
        'filter', 'list',
        *common_args,
        '--output', 'json',
    ])

    filters = json.loads(filters_json)
    assert len(filters) == len(default_filters)
