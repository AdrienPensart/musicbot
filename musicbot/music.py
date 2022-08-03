import itertools
import logging
import os
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
    def http_link(self) -> str:
        return f"http://{self.ipv4}/{self.path}"

    @property
    def ssh_link(self) -> str:
        return f"{self.user}@{self.ipv4}:{self.path}"

    def links(self, types: list[str]) -> frozenset[str]:
        paths = []
        if 'ssh' in types:
            paths.append(self.ssh_link)
        if 'local' in types:
            if os.path.isfile(self.path):
                paths.append(self.path)
        if 'http' in types:
            paths.append(self.http_link)
        return frozenset(paths)


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

    def links(self, types: list[str]) -> frozenset[str]:
        return frozenset(itertools.chain(*[folder.links(types) for folder in self.folders]))

    @property
    def slug(self) -> str:
        '''Slugify music'''
        return slugify(
            f"""{self.artist}-{self.title}""",
            stopwords=STOPWORDS,
            replacements=REPLACEMENTS,
        )
