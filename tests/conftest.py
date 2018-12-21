import pytest
import socket
import contextlib
import time
import os
from musicbot.backend import postgraphile, database
from . import fixtures


@pytest.fixture
def dbtest(worker_id):
    return database.DEFAULT_DB + "_test_" + worker_id


@pytest.fixture
def email_sample():
    worker_id = os.getenv('PYTEST_XDIST_WORKER', 'main')
    email_sample = (worker_id + "_" + fixtures.email)
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


@pytest.fixture
def postgraphile_public(postgres, unused_tcp_port_factory):
    public_port = unused_tcp_port_factory()
    print('New public postgraphile with port {} and db {}'.format(public_port, postgres.db))
    pql = postgraphile.Postgraphile.public(db=postgres.db, port=public_port)
    pql.run(background=True)
    time.sleep(1)
    yield pql
    pql.kill()


@pytest.fixture
def postgraphile_private(postgres, unused_tcp_port_factory):
    private_port = unused_tcp_port_factory()
    print('New private postgraphile with port {} and db {}'.format(private_port, postgres.db))
    pql = postgraphile.Postgraphile.private(db=postgres.db, port=private_port)
    pql.run(background=True)
    time.sleep(1)
    yield pql
    pql.kill()
