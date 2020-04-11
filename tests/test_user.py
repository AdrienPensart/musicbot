import logging
import json
import pytest
from musicbot import helpers
from musicbot.user import User, Admin
from musicbot.cli import cli
from . import fixtures
from .conftest import run_cli

logger = logging.getLogger(__name__)


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


@pytest.fixture
def files():
    files = helpers.genfiles(fixtures.folders)
    files = list(files)
    assert len(files) == 5
    return files


@pytest.yield_fixture
def user_sample(files, user_unregister, postgraphile_public):  # pylint: disable=unused-argument
    u = User.register(graphql=postgraphile_public, first_name=fixtures.first_name, last_name=fixtures.last_name, email=fixtures.email, password=fixtures.password)
    assert u.authenticated

    u.bulk_insert(files)
    for f in files:
        u.upsert_music(f)

    yield u
    u.unregister()
    assert not u.authenticated


@pytest.fixture
def musics(user_sample):
    musics = user_sample.do_filter()
    assert len(musics) == len(files)
    return musics


def test_list(user_sample, postgraphile_private):  # pylint: disable=unused-argument
    a = Admin(postgraphile_private)
    for user in a.users():
        if user['accountByUserId']['email'] == fixtures.email and user['firstName'] == fixtures.first_name and user['lastName'] == fixtures.last_name:
            break
    else:
        pytest.fail("test user not detected")


def test_delete(user_sample, files):
    user_sample.delete_music(files[0].path)
    musics = user_sample.do_filter()
    assert len(musics) == len(files) - 1


def test_authenticate(postgraphile_public, user_sample):
    assert user_sample.email == fixtures.email
    same1 = User(graphql=postgraphile_public, email=fixtures.email, password=fixtures.password)
    assert same1.authenticated
    assert same1.token

    same2 = User(graphql=postgraphile_public, token=same1.token)
    assert same2.authenticated

    same3 = User.new(graphql=postgraphile_public, email=fixtures.email, password=fixtures.password)
    assert same3.authenticated

    same3 = User.new(graphql=postgraphile_public, token=same1.token)
    assert same3.authenticated


def test_default_filters(user_sample):
    user_sample.load_default_filters()
    print(user_sample.filters)
    assert len(user_sample.filters) == fixtures.filters


def test_folders(user_sample):
    assert len(user_sample.folders) == len(fixtures.folders)
