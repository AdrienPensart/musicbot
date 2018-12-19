import logging
import pytest
import psycopg2
from musicbot.backend import database

logger = logging.getLogger(__name__)


@pytest.yield_fixture
def db(files, worker_id):
    db = database.DEFAULT_DB + "_test_" + worker_id
    database.create(db)
    return psycopg2.connect(db)
    database.drop(db)
