import logging
import pytest
import asyncio
import os

from lib import lib, file, mfilter
from lib.web.config import webconfig
from lib.config import config
from lib.web.app import create_app

logger = logging.getLogger(__name__)
webconfig.no_auth = True
config.set()

@pytest.yield_fixture
def loop():
    logger.debug('new event loop')
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.yield_fixture
def app(loop):
    logger.debug('new app')
    yield create_app()


@pytest.fixture
def test_cli(loop, app, test_client):
    logger.debug('new test client')
    return loop.run_until_complete(test_client(app))


async def test_index(test_cli):
    response = await test_cli.get('/')
    assert response.status == 200

async def test_collection_filters(test_cli):
    response = await test_cli.get('/collection/filters')
    assert response.status == 200
