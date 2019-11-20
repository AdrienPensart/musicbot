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
def test_admin(cli_runner, user_token, postgraphile_private):  # pylint: disable=unused-argument
    users = run_cli(cli_runner, cli, ['user', 'list', '--graphql-admin', postgraphile_private])
    assert len(users.split("\n")) == 1


@pytest.mark.runner_setup(mix_stderr=False)
def test_user(cli_runner, user_token, postgraphile_public):
    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public, 'load-default'])
    filters = run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public, 'list'])
    assert len(filters.split("\n")) == fixtures.filters

    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public, 'do'])
    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public, 'get', 'default'])

    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public, 'scan', *fixtures.folders])

    folders = run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public, 'list'])
    assert len(folders.split("\n")) == 2

    musics = run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public, 'find'])
    assert len(musics.split("\n")) == 5

    csv = run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public, 'csv'])
    assert len(csv.split("\n")) == 5

    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public, 'flac2mp3', '--dry'])
    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public, 'sync', '/tmp', '--dry'])
    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public, 'consistency'])

    playlist = run_cli(cli_runner, cli, ['playlist', '--token', user_token, '--graphql', postgraphile_public, 'new'])
    assert len(playlist.split("\n")) == 6

    run_cli(cli_runner, cli, ['playlist', '--token', user_token, '--graphql', postgraphile_public, 'bests', '/tmp'])
    run_cli(cli_runner, cli, ['stats', '--token', user_token, '--graphql', postgraphile_public, 'show'])

    run_cli(cli_runner, cli, ['genre', '--token', user_token, '--graphql', postgraphile_public, 'list'])
    run_cli(cli_runner, cli, ['artist', '--token', user_token, '--graphql', postgraphile_public, 'list'])
