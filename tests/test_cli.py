import logging
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
def test_admin(cli_runner, user_token, postgraphile_private_cli):  # pylint: disable=unused-argument
    users = run_cli(cli_runner, cli, ['user', 'list', '--graphql-admin', postgraphile_private_cli])
    assert len(users.split("\n")) == 1


@pytest.mark.runner_setup(mix_stderr=False)
def test_user(cli_runner, user_token, postgraphile_public_cli):
    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'load-default'])
    filters = run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'list'])
    assert len(filters.split("\n")) == fixtures.filters

    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'do'])
    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'get', 'default'])

    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'scan', *fixtures.folders])

    folders = run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'list'])
    assert len(folders.split("\n")) == 2

    musics = run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'find'])
    assert len(musics.split("\n")) == 5

    csv = run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'csv'])
    assert len(csv.split("\n")) == 5

    run_cli(cli_runner, cli, ['--dry', 'folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'flac2mp3'])
    run_cli(cli_runner, cli, ['--dry', 'folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'sync', '/tmp'])
    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'consistency'])

    playlist = run_cli(cli_runner, cli, ['playlist', '--token', user_token, '--graphql', postgraphile_public_cli, 'new'])
    assert len(playlist.split("\n")) == 6

    run_cli(cli_runner, cli, ['--dry', 'playlist', '--token', user_token, '--graphql', postgraphile_public_cli, 'bests', '/tmp'])
    run_cli(cli_runner, cli, ['stats', '--token', user_token, '--graphql', postgraphile_public_cli, 'show'])

    run_cli(cli_runner, cli, ['genre', '--token', user_token, '--graphql', postgraphile_public_cli, 'list'])
    run_cli(cli_runner, cli, ['artist', '--token', user_token, '--graphql', postgraphile_public_cli, 'list'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_db(cli_runner, db_cli):
    run_cli(cli_runner, cli, ['db', 'clear', '--yes', '--db', db_cli])
