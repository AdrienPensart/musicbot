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
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'load-filters'])
    filters_json = run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'filters', '--output', 'json'])
    filters = json.loads(filters_json)
    assert len(filters) == fixtures.filters

    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'filter', 'default'])
    # run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'tracks'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'scan', *fixtures.folders])

    folders_json = run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'folders', '--output', 'json'])
    folders = json.loads(folders_json)
    assert len(folders) == 2

    musics = run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'find'])
    assert len(musics.split("\n")) == 5

    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'flac2mp3', '--dry'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'sync', '/tmp', '--dry'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'consistency'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'playlist', '--output', 'csv'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'playlist', '--output', 'json'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'playlist', '--output', 'table'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'playlist', '--output', 'm3u'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'bests', '/tmp', '--dry'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'stats'])
    run_cli(cli_runner, cli, ['local', '--token', user_token, '--graphql', postgraphile_public, 'artists'])
