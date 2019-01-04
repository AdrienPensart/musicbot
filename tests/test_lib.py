import logging
import pytest
from musicbot import lib

logger = logging.getLogger(__name__)


def test_str2bool():
    assert lib.str2bool('Y')
    assert not lib.str2bool('N')
    with pytest.raises(Exception):
        lib.str2bool('whatever')
