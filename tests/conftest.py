# type: ignore
import time
import json
import socket
import logging

import pytest
from click_skeleton.testing import run_cli

from musicbot.main import cli

from . import fixtures

logger = logging.getLogger(__name__)

pytest_plugins = ["docker_compose"]


def wait_for_service(service, timeout=60):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((service.hostname, service.host_port), timeout=timeout):
                break
        except OSError as e:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(f'Waited too long for the port {service.host_port} on host {service.hostname} to start accepting connections.') from e


@pytest.fixture
def edgedb(function_scoped_container_getter):
    service = function_scoped_container_getter.get("edgedb").network_info[0]
    dsn = f"""edgedb://edgedb:musicbot@{service.hostname}:{service.host_port}"""
    wait_for_service(service)
    return dsn


@pytest.fixture(scope="session")
def testmusics(cli_runner, edgedb):
    output = run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'scan',
        '--clean',
        '--dsn', edgedb,
        '--output', 'json',
        *fixtures.folders,
    ])
    json.loads(output)
    yield output
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'clean',
        '--dsn', edgedb,
        '--yes',
    ])
