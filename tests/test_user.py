import pytest
import os
import logging
import signal
import subprocess
import time
from musicbot import user, helpers
from musicbot.backend import postgraphile
from . import fixtures

logger = logging.getLogger(__name__)


email = "test@test.com"
password = "test_test"

os.environ['MB_GRAPHQL_PUBLIC_PORT'] = str(10000)
os.environ['MB_GRAPHQL_PRIVATE_PORT'] = str(10001)
os.environ['MB_GRAPHQL'] = "http://127.0.0.1:10000/graphql"
os.environ['MB_GRAPHQL_ADMIN'] = "http://127.0.0.1:10001/graphql"


@pytest.fixture
def postgraphile_public():
    cmd = postgraphile.public(graphql_public_port=10000)
    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    time.sleep(1)
    yield pro
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)


@pytest.fixture
def postgraphile_private():
    cmd = postgraphile.private(graphql_private_port=10001)
    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    yield pro
    time.sleep(1)
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)


@pytest.fixture
def files():
    files = helpers.genfiles(fixtures.folders)
    assert len(files) == 5
    return files


@pytest.fixture
def email_sample():
    worker_id = os.environ['PYTEST_XDIST_WORKER']
    email_sample = (worker_id + "_" + email)
    return email_sample


@pytest.fixture()
def user_sample(worker_id, email_sample, files, postgraphile_public, postgraphile_private):
    u = user.User.register(graphql=os.environ['MB_GRAPHQL'], first_name="first_test", last_name="last_test", email=email_sample, password=password)
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
