import logging
from musicbot import helpers

logger = logging.getLogger(__name__)


def test_password():
    assert helpers.random_password() != helpers.random_password()
