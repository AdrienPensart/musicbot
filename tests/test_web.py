import logging
import os
import asyncio
import pytest

from musicbot.lib.database import MB_DB, DEFAULT_DB
from musicbot.lib.web.config import webconfig
from musicbot.lib.config import config
from musicbot.lib.web.app import create_app

logger = logging.getLogger(__name__)
webconfig.no_auth = True
config.set()


@pytest.yield_fixture
def loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.yield_fixture
async def app(loop, worker_id):
    db = os.getenv(MB_DB, DEFAULT_DB)
    db += ("_" + worker_id)
    app = create_app(db=db)
    yield app
    await app.db.drop()


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


async def test_index(test_cli):
    response = await test_cli.get('/')
    assert response.status == 200


async def test_collection_filters(test_cli):
    response = await test_cli.get('/collection/filters')
    assert response.status == 200
