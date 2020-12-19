import json
import pytest
from click_skeleton.testing import run_cli
from musicbot.cli import main_cli
from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_show(cli_runner, common_args):
    run_cli(cli_runner, main_cli, [
        '--quiet',
        'filter', 'show',
        *common_args,
        'default',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_delete(cli_runner, common_args):
    run_cli(cli_runner, main_cli, [
        '--quiet',
        'filter', 'delete',
        *common_args,
        'default',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_count(cli_runner, common_args):
    count_filters_str = run_cli(cli_runner, main_cli, [
        '--quiet',
        'filter', 'count',
        *common_args,
    ])
    count_filters = int(count_filters_str)
    assert count_filters == 15


@pytest.mark.runner_setup(mix_stderr=False)
def test_filter_list(cli_runner, common_args):
    filters_json = run_cli(cli_runner, main_cli, [
        '--quiet',
        'filter', 'list',
        *common_args,
        '--output', 'json',
    ])

    filters = json.loads(filters_json)
    assert len(filters) == fixtures.filters
