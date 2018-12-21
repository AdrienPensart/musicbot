import logging
from musicbot import lib
from musicbot.music import file, youtube
from . import fixtures

logger = logging.getLogger(__name__)


def test_finding_files():
    files = list(lib.find_files([fixtures.folder1, fixtures.folder2]))
    assert len(files) == 5


def test_flac_tags():
    m = file.File(fixtures.one_flac, fixtures.folder1)

    assert m.artist == "Buckethead"
    assert m.title == "Welcome To Bucketheadland"
    assert m.album == "Giant Robot"
    assert m.genre == "Avantgarde"
    assert m.number == 2
    assert m.description == "rock cutoff"
    assert m.keywords == "rock cutoff"
    assert m.rating == 5.0
    assert m.duration == 1


def test_mp3_tags():
    m = file.File(fixtures.one_mp3, fixtures.folder2)

    assert m.artist == "1995"
    assert m.title == "La Flemme"
    assert m.album == "La Source"
    assert m.genre == "Rap"
    assert m.number == 2
    assert m.comment == "rap french"
    assert m.keywords == "rap french"
    assert m.rating == 4.5
    assert m.duration == 258

    assert youtube.search(m.artist, m.title, 258) == 'https://www.youtube.com/watch?v=JyjQFMksvaM'


def test_duration():
    assert 12 == lib.duration_to_seconds("12s")
    assert 60 * 12 == lib.duration_to_seconds("12m")
    assert 60 * 60 * 12 == lib.duration_to_seconds("12h")


def test_raise_limits():
    assert lib.raise_limits() is True
