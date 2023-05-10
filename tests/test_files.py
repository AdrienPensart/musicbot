import logging

from beartype import beartype
from musicbot.file import File

from . import fixtures

logger = logging.getLogger(__name__)


@beartype
def test_flac_tags() -> None:
    m = File.from_path(folder=fixtures.folder_flac, path=fixtures.one_flac)
    assert m
    assert m.artist == "Buckethead"
    assert m.title == "Welcome To Bucketheadland"
    assert m.album == "Giant Robot"
    assert m.genre == "Avantgarde"
    assert m.track == 2
    assert m._description == "rock cutoff"
    assert m.keywords == {"rock", "cutoff"}
    assert m.rating == 5.0
    assert m.length == 1


@beartype
def test_mp3_tags() -> None:
    m = File.from_path(folder=fixtures.folder_mp3, path=fixtures.one_mp3)
    assert m
    assert m.artist == "1995"
    assert m.title == "La Flemme"
    assert m.album == "La Source"
    assert m.genre == "Rap"
    assert m.track == 2
    assert m._comment == "rap french"
    assert m.keywords == {"rap", "french"}
    assert m.rating == 4.5
    assert m.length == 258
