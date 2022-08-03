import itertools
import logging
import sys
from typing import Any

import yaml
from attr import asdict, frozen
from beartype import beartype
from slugify import slugify

from musicbot.defaults import REPLACEMENTS, STOPWORDS
from musicbot.helpers import bytes_to_human, precise_seconds_to_human
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@frozen(repr=False)
class Folder(MusicbotObject):
    name: str
    ipv4: str
    user: str
    path: str

    def __repr__(self) -> str:
        return f"{self.name} {self.ipv4} {self.user}"

    @property
    def links(self) -> frozenset[str]:
        return frozenset({self.path})


@frozen
class Music(MusicbotObject):
    title: str
    album: str
    artist: str
    genre: str
    track: int
    size: int
    rating: float
    length: int
    keywords: frozenset[str]
    folders: frozenset[Folder]
    # youtube: str | None
    # spotify: str | None

    @beartype
    def human_repr(self) -> str:
        data: dict[str, Any] = asdict(self)
        data['size'] = bytes_to_human(data['size'])
        data['length'] = precise_seconds_to_human(data['length'])
        return yaml.dump(data, sort_keys=False, width=sys.maxsize)

    @property
    def links(self) -> frozenset[str]:
        return frozenset(itertools.chain(*[folder.links for folder in self.folders]))

    @property
    def slug(self) -> str:
        '''Slugify music'''
        return slugify(
            f"""{self.artist}-{self.title}""",
            stopwords=STOPWORDS,
            replacements=REPLACEMENTS,
        )
