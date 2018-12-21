import signal
import os
import traceback
import logging
import pytest
import time
from musicbot.cli import cli, main
from musicbot.commands import config, completion, db, user
from . import fixtures

logger = logging.getLogger(__name__)


def run_cli(cli_runner, called_cli, *args):
    result = cli_runner.invoke(called_cli, *args)
    logger.debug(result.output)
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    return result.output


@pytest.yield_fixture
def db_cli(cli_runner, dbtest):
    run_cli(cli_runner, db.cli, ['create', '--db', dbtest])
    yield dbtest
    run_cli(cli_runner, db.cli, ['drop', '--yes', '--db', dbtest])


@pytest.yield_fixture
def postgraphile_public_cli(cli_runner, db_cli, unused_tcp_port_factory):
    port = str(unused_tcp_port_factory())
    public_group = run_cli(cli_runner, cli, ['--debug', 'postgraphile', 'public', 'my_testing_secret', '--background', '--db', db_cli, '--graphql-public-port', port])
    # public_group = run_cli(cli_runner, cli, ['postgraphile', 'public', 'my_testing_secret', '--background', '--db', db_cli, '--graphql-public-port', port])
    time.sleep(1)
    yield "http://127.0.0.1:{}/graphql".format(port)
    os.killpg(int(public_group), signal.SIGTERM)


@pytest.yield_fixture
def postgraphile_private_cli(cli_runner, db_cli, unused_tcp_port_factory):
    port = str(unused_tcp_port_factory())
    private_group = run_cli(cli_runner, cli, ['--debug', 'postgraphile', 'private', '--background', '--db', db_cli, '--graphql-private-port', port])
    # private_group = run_cli(cli_runner, cli, ['postgraphile', 'private', '--background', '--db', db_cli, '--graphql-private-port', port])
    time.sleep(1)
    yield "http://127.0.0.1:{}/graphql".format(port)
    os.killpg(int(private_group), signal.SIGTERM)


@pytest.yield_fixture
def user_token(cli_runner, email_sample, postgraphile_public_cli):
    run_cli(cli_runner, user.cli, ['register', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password])
    token = run_cli(cli_runner, user.cli, ['login', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password])
    token = token.rstrip()
    yield token
    run_cli(cli_runner, user.cli, ['unregister', '--graphql', postgraphile_public_cli, '--token', token])


@pytest.mark.runner_setup(mix_stderr=False)
def test_cli(cli_runner):
    main(standalone_mode=False)
    run_cli(cli_runner, cli)
    run_cli(cli_runner, cli, ['-V'])
    run_cli(cli_runner, cli, ['--help'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_config(cli_runner):
    run_cli(cli_runner, config.cli, ['show'])
    run_cli(cli_runner, config.cli, ['logging'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_completion(cli_runner):
    run_cli(cli_runner, completion.cli, ['show', 'zsh'])
    run_cli(cli_runner, completion.cli, ['show', 'bash'])
    run_cli(cli_runner, completion.cli, ['install', 'zsh'])
    run_cli(cli_runner, completion.cli, ['install', 'bash'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_user(cli_runner, user_token, postgraphile_public_cli, postgraphile_private_cli):
    run_cli(cli_runner, user.cli, ['login', '--graphql', postgraphile_public_cli, '--token', user_token])
    run_cli(cli_runner, user.cli, ['list', '--graphql-admin', postgraphile_private_cli])

    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'load-default'])
    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'list'])
    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'do'])
    run_cli(cli_runner, cli, ['filter', '--token', user_token, '--graphql', postgraphile_public_cli, 'get', 'default'])

    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'scan', *fixtures.folders])
    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'list'])
    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'find'])
    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'csv'])
    run_cli(cli_runner, cli, ['--dry', 'folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'flac2mp3'])
    run_cli(cli_runner, cli, ['--dry', 'folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'sync', '/tmp'])
    run_cli(cli_runner, cli, ['folder', '--token', user_token, '--graphql', postgraphile_public_cli, 'consistency'])

    run_cli(cli_runner, cli, ['playlist', '--token', user_token, '--graphql', postgraphile_public_cli, 'new'])
    run_cli(cli_runner, cli, ['playlist', '--token', user_token, '--graphql', postgraphile_public_cli, 'bests', '/tmp'])

    run_cli(cli_runner, cli, ['stats', '--token', user_token, '--graphql', postgraphile_public_cli, 'show'])


def test_db(cli_runner, db_cli):
    run_cli(cli_runner, db.cli, ['clear', '--yes', '--db', db_cli])
