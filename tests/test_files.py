import logging
from musicbot.music import file
from . import fixtures

logger = logging.getLogger(__name__)


def test_flac_tags():
    m = file.File(fixtures.one_flac, fixtures.folder1)
    assert m.artist == "Buckethead"
    assert m.title == "Welcome To Bucketheadland"
    assert m.album == "Giant Robot"
    assert m.genre == "Avantgarde"
    assert m.number == 2
    assert m._description == "rock cutoff"
    assert m.keywords == ['rock', 'cutoff']
    assert m.rating == 5.0
    assert m.duration == 1


def test_mp3_tags():
    m = file.File(fixtures.one_mp3, fixtures.folder2)
    assert m.artist == "1995"
    assert m.title == "La Flemme"
    assert m.album == "La Source"
    assert m.genre == "Rap"
    assert m.number == 2
    assert m._comment == "rap french"
    assert m.keywords == ['rap', 'french']
    assert m.rating == 4.5
    assert m.duration == 258
