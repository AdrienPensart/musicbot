import socket
import time
import traceback
import logging
import pytest
from musicbot.cli import cli, prog_name
from . import fixtures

logger = logging.getLogger(__name__)
pytest_plugins = ["docker_compose"]


def wait_for_service(service, timeout=60):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((service.hostname, service.host_port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(f'Waited too long for the port {service.host_port} on host {service.hostname} to start accepting connections.') from ex


def run_cli(cli_runner, called_cli, *args):
    if args:
        logger.debug('Invoking : %s %s', prog_name, ' '.join(str(elem) for elem in args))
    result = cli_runner.invoke(called_cli, *args)
    logger.debug(result.output)
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    return result.output.rstrip()


@pytest.fixture
def db(function_scoped_container_getter):
    service = function_scoped_container_getter.get("db").network_info[0]
    db_dsn = f"postgresql://postgres:musicbot@{service.hostname}:{service.host_port}/musicbot"
    wait_for_service(service)
    return db_dsn


@pytest.fixture
def postgraphile_public(db, function_scoped_container_getter):  # pylint: disable=unused-argument
    service = function_scoped_container_getter.get("postgraphile_public").network_info[0]
    time.sleep(10)
    wait_for_service(service)
    return f"http://{service.hostname}:{service.host_port}/graphql"


@pytest.fixture
def postgraphile_private(db, function_scoped_container_getter):  # pylint: disable=unused-argument
    service = function_scoped_container_getter.get("postgraphile_private").network_info[0]
    time.sleep(10)
    wait_for_service(service)
    return f"http://{service.hostname}:{service.host_port}/graphql"


@pytest.yield_fixture
def user_token(cli_runner, postgraphile_public):
    run_cli(cli_runner, cli, ['user', 'register', '--graphql', postgraphile_public, '--email', fixtures.email, '--password', fixtures.password, '--first-name', fixtures.first_name, '--last-name', fixtures.last_name])
    token = run_cli(cli_runner, cli, ['user', 'token', '--graphql', postgraphile_public, '--email', fixtures.email, '--password', fixtures.password])
    token = token.rstrip()
    return token
