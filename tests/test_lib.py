import logging
import pytest
from musicbot import lib
from musicbot.music.file import supported_formats
from . import fixtures

logger = logging.getLogger(__name__)


def test_str2bool():
    assert lib.str2bool('Y')
    assert not lib.str2bool('N')
    with pytest.raises(Exception):
        lib.str2bool('whatever')


def test_finding_files():
    files = list(lib.find_files([fixtures.folder1, fixtures.folder2], supported_formats))
    assert len(files) == 5
