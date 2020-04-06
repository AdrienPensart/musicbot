import logging
import json
import pytest
from musicbot import version
from musicbot.cli import cli
from . import fixtures
from .conftest import run_cli

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli(cli_runner):
    run_cli(cli_runner, cli)


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_version(cli_runner):
    output1 = run_cli(cli_runner, cli, ['-V'])
    output2 = run_cli(cli_runner, cli, ['--version'])
    output3 = run_cli(cli_runner, cli, ['version'])
    assert output1 == output2 == output3
    assert version.__version__ in output1


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli_help(cli_runner):
    output1 = run_cli(cli_runner, cli, ['-h'])
    output2 = run_cli(cli_runner, cli, ['--help'])
    output3 = run_cli(cli_runner, cli, ['help'])
    assert output1 == output2 == output3


@pytest.mark.runner_setup(mix_stderr=False)
def test_config(cli_runner):
    run_cli(cli_runner, cli, ['config', 'show'])
    run_cli(cli_runner, cli, ['config', 'logging'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_admin(cli_runner, user_token, postgraphile_private):  # pylint: disable=unused-argument
    users_json = run_cli(cli_runner, cli, ['user', 'list', '--output', 'json', '--graphql-admin', postgraphile_private])
    users = json.loads(users_json)
    assert len(users) == 1


@pytest.mark.runner_setup(mix_stderr=False)
def test_user(cli_runner, user_token, postgraphile_public):
    common_args = ['--token', user_token, '--graphql', postgraphile_public]

    run_cli(cli_runner, cli, ['local', *common_args, 'load-filters'])
    filters_json = run_cli(cli_runner, cli, ['local', *common_args, 'filters', '--output', 'json'])
    filters = json.loads(filters_json)
    assert len(filters) == fixtures.filters

    run_cli(cli_runner, cli, ['local', *common_args, 'filter', 'default'])
    run_cli(cli_runner, cli, ['local', *common_args, 'scan', *fixtures.folders])

    folders_json = run_cli(cli_runner, cli, ['local', *common_args, 'folders', '--output', 'json'])
    folders = json.loads(folders_json)
    assert len(folders) == 2

    musics = run_cli(cli_runner, cli, ['local', *common_args, 'find'])
    assert len(musics.split("\n")) == 5

    run_cli(cli_runner, cli, ['local', *common_args, 'sync', '/tmp', '--dry'])
    run_cli(cli_runner, cli, ['local', *common_args, 'consistency'])
    run_cli(cli_runner, cli, ['local', *common_args, 'playlist', '--output', 'csv'])
    run_cli(cli_runner, cli, ['local', *common_args, 'playlist', '--output', 'json'])
    run_cli(cli_runner, cli, ['local', *common_args, 'playlist', '--output', 'table'])
    run_cli(cli_runner, cli, ['local', *common_args, 'playlist', '--output', 'm3u'])
    run_cli(cli_runner, cli, ['local', *common_args, 'bests', '/tmp', '--dry'])
    run_cli(cli_runner, cli, ['local', *common_args, 'stats'])
    run_cli(cli_runner, cli, ['local', *common_args, 'artists'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_folder(cli_runner):
    run_cli(cli_runner, cli, ['folder', 'flac2mp3', '--dry', *fixtures.folders])
    run_cli(cli_runner, cli, ['folder', 'tracks', *fixtures.folders])
