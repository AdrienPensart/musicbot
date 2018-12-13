import os
import logging
import pytest
from musicbot.lib.database import MB_DB, DEFAULT_DB, Database
from musicbot.lib import lib
from . import fixtures

logger = logging.getLogger(__name__)


@pytest.fixture
def files():
    return list(lib.find_files(fixtures.folders))


@pytest.yield_fixture
async def db(files, worker_id):
    # if running pytest with xdist
    # append worker ID to test database name
    db_name = os.getenv(MB_DB, DEFAULT_DB)
    db_name += ("_" + worker_id)
    db = await Database.make(db=db_name)
    await db.clear()
    yield db
    await db.drop()
