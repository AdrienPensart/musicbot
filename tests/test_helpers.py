import logging
from musicbot import helpers
from musicbot.music.file import supported_formats
from musicbot.music.helpers import find_files
from . import fixtures

logger = logging.getLogger(__name__)


def test_password():
    assert helpers.random_password() != helpers.random_password()


def test_finding_files():
    files = list(find_files([fixtures.folder1, fixtures.folder2], supported_formats))
    assert len(files) == 5
