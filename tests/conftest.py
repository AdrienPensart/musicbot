import socket
import signal
import os
import time
import contextlib
import traceback
import logging
import pytest
from musicbot.backend import postgraphile, database
from musicbot.cli import cli, prog_name
from . import fixtures

logger = logging.getLogger(__name__)


def run_cli(cli_runner, called_cli, *args):
    if args:
        logger.debug('Invoking : %s %s', prog_name, ' '.join(*args))
    result = cli_runner.invoke(called_cli, *args)
    logger.debug(result.output)
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    return result.output.rstrip()


@pytest.fixture
def my_worker_id():
    return os.getenv('PYTEST_XDIST_WORKER', 'main')


@pytest.fixture
def dbtest(my_worker_id):
    return database.DEFAULT_DB + "_test_" + my_worker_id


@pytest.fixture
def email_sample(my_worker_id):
    email_sample = "{}_{}".format(my_worker_id, fixtures.email)
    # test = os.getenv('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
    # import string
    # from random import choice
    # allchar = string.ascii_letters + string.digits
    # test = "".join(choice(allchar) for x in range(12))
    # email_sample = "{}_{}_{}".format(my_worker_id, test, fixtures.email)
    return email_sample


def _unused_tcp_port(interface='127.0.0.1'):
    """Find an unused localhost TCP port from 1024-65535 and return it."""
    with contextlib.closing(socket.socket()) as sock:
        sock.bind((interface, 0))
        return sock.getsockname()[1]


@pytest.fixture
def unused_tcp_port():
    return _unused_tcp_port()


@pytest.fixture
def unused_tcp_port_factory():
    """A factory function, producing different unused TCP ports."""
    produced = set()

    def factory():
        """Return an unused port."""
        port = _unused_tcp_port()
        while port in produced:
            port = _unused_tcp_port()
        produced.add(port)
        return port
    return factory


@pytest.yield_fixture
def postgres(dbtest):
    pg = database.Database(dbtest)
    pg.create()
    yield pg
    pg.drop()


@pytest.yield_fixture
def postgraphile_public(postgres, unused_tcp_port_factory):
    public_port = unused_tcp_port_factory()
    pql = postgraphile.Postgraphile.public(db=postgres.db, port=public_port)
    pql.run(background=True)
    time.sleep(15)
    yield pql
    pql.kill()


@pytest.yield_fixture
def postgraphile_private(postgres, unused_tcp_port_factory):
    private_port = unused_tcp_port_factory()
    pql = postgraphile.Postgraphile.private(db=postgres.db, port=private_port)
    pql.run(background=True)
    time.sleep(15)
    yield pql
    pql.kill()


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
    time.sleep(15)
    yield "http://127.0.0.1:{}/graphql".format(port)
    os.killpg(int(public_group), signal.SIGTERM)


@pytest.yield_fixture
def postgraphile_private_cli(cli_runner, db_cli, unused_tcp_port_factory):
    port = str(unused_tcp_port_factory())
    # private_group = run_cli(cli_runner, cli, ['--debug', 'postgraphile', 'private', '--background', '--db', db_cli, '--graphql-private-port', port])
    private_group = run_cli(cli_runner, cli, ['postgraphile', 'private', '--background', '--db', db_cli, '--graphql-private-port', port])
    time.sleep(15)
    yield "http://127.0.0.1:{}/graphql".format(port)
    os.killpg(int(private_group), signal.SIGTERM)


@pytest.yield_fixture
def user_token(cli_runner, email_sample, postgraphile_public_cli):
    run_cli(cli_runner, cli, ['user', 'register', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password, '--first-name', fixtures.first_name, '--last-name', fixtures.last_name])
    token = run_cli(cli_runner, cli, ['user', 'login', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password])
    token = token.rstrip()
    yield token
    run_cli(cli_runner, cli, ['user', 'unregister', '--graphql', postgraphile_public_cli, '--email', email_sample, '--password', fixtures.password])
