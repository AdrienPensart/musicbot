import pytest
import os
import logging
from musicbot.lib import user, musicbot
from . import fixtures

logger = logging.getLogger(__name__)


email = "test@test.com"
password = "test_test"


@pytest.fixture
def files():
    files = musicbot.genfiles(fixtures.folders)
    assert len(files) == 5
    return files


@pytest.fixture
def email_sample():
    worker_id = os.environ['PYTEST_XDIST_WORKER']
    email_sample = (worker_id + "_" + email)
    return email_sample


@pytest.fixture()
def user_sample(worker_id, email_sample, files):
    u = user.User.register(graphql=user.DEFAULT_GRAPHQL, first_name="first_test", last_name="last_test", email=email_sample, password=password)
    assert u.authenticated

    u.bulk_insert(files)
    for f in files:
        u.upsert_music(f)

    yield u
    u.unregister()
    assert not u.authenticated


@pytest.fixture()
def musics(user_sample):
    musics = user_sample.do_filter()
    assert len(musics) == len(files)


def test_delete(user_sample, files):
    user_sample.delete_music(files[1].path)
    musics = user_sample.do_filter()
    assert len(musics) == len(files) - 1


def test_authenticate(user_sample, email_sample):
    same1 = user.User(email=email_sample, password=password)
    assert same1.authenticated
    assert same1.token

    same2 = user.User(token=same1.token)
    assert same2.authenticated

    same3 = user.User.new(email=email_sample, password=password)
    assert same3.authenticated

    same3 = user.User.new(token=same1.token)
    assert same3.authenticated


def test_default_filters(user_sample):
    user_sample.load_default_filters()
    print(user_sample.filters)
    assert len(user_sample.filters) == 11


def test_folders(user_sample):
    assert len(user_sample.folders) == len(fixtures.folders)
