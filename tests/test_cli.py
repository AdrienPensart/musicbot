import signal
import os
import traceback
import logging
import pytest
import time
from musicbot import version
from musicbot.cli import cli
from . import fixtures

logger = logging.getLogger(__name__)


def run_cli(cli_runner, called_cli, *args):
    result = cli_runner.invoke(called_cli, *args)
    logger.debug(result.output)
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    return result.output.rstrip()


@pytest.yield_fixture
def db_cli(cli_runner, dbtest):
    run_cli(cli_runner, cli, ['db', 'clear', '--yes', '--db', dbtest])
    yield dbtest
    run_cli(cli_runner, cli, ['db', 'drop', '--yes', '--db', dbtest])


@pytest.yield_fixture
def postgraphile_public_cli(cli_runner, db_cli, unused_tcp_port_factory):
    port = str(unused_tcp_port_factory())
    # public_group = run_cli(cli_runner, cli, ['--debug', 'postgraphile', 'public', 'my_testing_secret', '--background', '--db', db_cli, '--graphql-public-port', port])
    public_group = run_cli(cli_runner, cli, ['postgraphile', 'public', 'my_testing_secret', '--background', '--db', db_cli, '--graphql-public-port', port])
    time.sleep(1)
    yield "http://127.0.0.1:{}/graphql".format(port)
    os.killpg(int(public_group), signal.SIGTERM)


@pytest.yield_fixture
def postgraphile_private_cli(cli_runner, db_cli, unused_tcp_port_factory):
    port = str(unused_tcp_port_factory())
    # private_group = run_cli(cli_runner, cli, ['--debug', 'postgraphile', 'private', '--background', '--db', db_cli, '--graphql-private-port', port])
    private_group = run_cli(cli_runner, cli, ['postgraphile', 'private', '--background', '--db', db_cli, '--graphql-private-port', port])
    time.sleep(1)
    yield "http://127.0.0.1:{}/graphql".format(port)
    os.killpg(int(private_group), signal.SIGTERM)


@pytest.yield_fixture
def user_token(cli_runner, email_sample, postgraphile_public_cli):
    run_cli(cli_runner, cli, ['user', 'register', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password, '--first-name', fixtures.first_name, '--last-name', fixtures.last_name])
    token = run_cli(cli_runner, cli, ['user', 'login', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password])
    token = token.rstrip()
    yield token
    run_cli(cli_runner, cli, ['user', 'unregister', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password])


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


# @pytest.mark.runner_setup(mix_stderr=False)
# def test_completion(cli_runner):
#     run_cli(cli_runner, cli, ['completion', 'show', 'zsh'])
#     run_cli(cli_runner, cli, ['completion', 'show', 'bash'])
#     run_cli(cli_runner, cli, ['completion', 'install', 'zsh'])
#     run_cli(cli_runner, cli, ['completion', 'install', 'bash'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_admin(cli_runner, user_token, postgraphile_private_cli):
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
