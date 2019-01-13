import socket
import time
import os
import contextlib
import pytest
from musicbot.backend import postgraphile, database
from . import fixtures


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
    print('New public postgraphile with port {} and db {}'.format(public_port, postgres.db))
    pql = postgraphile.Postgraphile.public(db=postgres.db, port=public_port)
    pql.run(background=True)
    time.sleep(1)
    yield pql
    pql.kill()


@pytest.yield_fixture
def postgraphile_private(postgres, unused_tcp_port_factory):
    private_port = unused_tcp_port_factory()
    print('New private postgraphile with port {} and db {}'.format(private_port, postgres.db))
    pql = postgraphile.Postgraphile.private(db=postgres.db, port=private_port)
    pql.run(background=True)
    time.sleep(1)
    yield pql
    pql.kill()
