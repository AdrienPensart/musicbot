import logging
import pytest
from musicbot import user, helpers
from . import fixtures

logger = logging.getLogger(__name__)


@pytest.fixture
def files():
    files = helpers.genfiles(fixtures.folders)
    files = list(files)
    assert len(files) == 5
    return files


@pytest.yield_fixture
def user_sample(email_sample, files, postgraphile_public):
    u = user.User.register(graphql=postgraphile_public.dsn, first_name=fixtures.first_name, last_name=fixtures.last_name, email=email_sample, password=fixtures.password)
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
    a = user.Admin(postgraphile_private.dsn)
    assert len(a.users()) == 1


def test_delete(user_sample, files):
    user_sample.delete_music(files[0].path)
    musics = user_sample.do_filter()
    assert len(musics) == len(files) - 1


def test_authenticate(postgraphile_public, user_sample, email_sample):
    same1 = user.User(graphql=postgraphile_public.dsn, email=email_sample, password=fixtures.password)
    assert same1.authenticated
    assert same1.token

    same2 = user.User(graphql=postgraphile_public.dsn, token=same1.token)
    assert same2.authenticated

    same3 = user.User.new(graphql=postgraphile_public.dsn, email=email_sample, password=fixtures.password)
    assert same3.authenticated

    same3 = user.User.new(graphql=postgraphile_public.dsn, token=same1.token)
    assert same3.authenticated


def test_default_filters(user_sample):
    user_sample.load_default_filters()
    print(user_sample.filters)
    assert len(user_sample.filters) == fixtures.filters


def test_folders(user_sample):
    assert len(user_sample.folders) == len(fixtures.folders)
