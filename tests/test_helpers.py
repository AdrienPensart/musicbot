import logging
from musicbot import helpers

logger = logging.getLogger(__name__)


def test_finding_files():
    assert helpers.random_password() != helpers.random_password()
