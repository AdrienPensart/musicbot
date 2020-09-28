import socket
import time
import logging
from typing import Collection
import pytest
from click_skeleton.testing import run_cli
from musicbot.cli import main_cli
from musicbot.helpers import genfiles
from musicbot.user import User
from musicbot.music.file import File
from musicbot.exceptions import FailedAuthentication
from . import fixtures

logger = logging.getLogger(__name__)
pytest_plugins = ["docker_compose"]


# import os
# def pytest_generate_tests(metafunc):  # pylint: disable=unused-argument
#     os.environ['MB_CONFIG'] = '/tmp/musicbot.ini'


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
def user_unregister(postgraphile_public):
    try:
        user = User.from_auth(graphql=postgraphile_public, email=fixtures.email, password=fixtures.password)
        user.unregister()
    except FailedAuthentication as e:
        logger.warning(f"Test user did not exist : {e}")


@pytest.yield_fixture
def user_token(cli_runner, postgraphile_public, user_unregister):  # pylint: disable=unused-argument
    run_cli(cli_runner, main_cli, [
        'user', 'register',
        '--graphql', postgraphile_public,
        '--email', fixtures.email,
        '--password', fixtures.password,
        '--first-name', fixtures.first_name,
        '--last-name', fixtures.last_name
    ])
    token = run_cli(cli_runner, main_cli, [
        'user', 'token',
        '--graphql', postgraphile_public,
        '--email', fixtures.email,
        '--password', fixtures.password
    ])
    token = token.rstrip()
    assert token.count('\n') == 0
    return token


@pytest.fixture
def files() -> Collection[File]:
    files = genfiles(fixtures.folders)
    files = list(files)
    assert len(files) == 5
    return files


@pytest.yield_fixture
def user_sample(files, user_unregister, postgraphile_public):  # pylint: disable=unused-argument
    u = User.register(graphql=postgraphile_public, first_name=fixtures.first_name, last_name=fixtures.last_name, email=fixtures.email, password=fixtures.password)
    u.bulk_insert(files)
    for f in files:
        u.upsert_music(f)

    yield u
    u.unregister()


@pytest.fixture
def musics(user_sample, files):
    musics = user_sample.do_filter()
    len_musics = len(musics)
    len_files = len(files)
    assert len_musics == len_files
    return musics


@pytest.fixture
def common_args(user_token, postgraphile_public):
    return ['--token', user_token, '--graphql', postgraphile_public]


@pytest.fixture
def user_musics(cli_runner, common_args):
    run_cli(cli_runner, main_cli, ['local', 'scan', *common_args, *fixtures.folders])
