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
from musicbot.helpers import (
    bytes_to_human,
    get_public_ip,
    precise_seconds_to_human
)
from musicbot.object import MusicbotObject
from musicbot.playlist_options import PlaylistOptions

logger = logging.getLogger(__name__)


@frozen(repr=False)
class Folder(MusicbotObject):
    name: str
    ipv4: str
    user: str
    path: str

    def __repr__(self) -> str:
        return f"{self.name} {self.ipv4} {self.user}"

    def effective_path(self, relative: bool = False) -> str:
        if relative:
            return self.path[len(self.name) + 1:]
        return self.path

    def http_link(self, relative: bool = False) -> str:
        return f"http://{self.ipv4}/{self.effective_path(relative)}"

    def ssh_link(self) -> str:
        return f"{self.user}@{self.ipv4}:{self.path}"

    def links(self, playlist_options: PlaylistOptions) -> frozenset[str]:
        paths = []
        if 'all' in playlist_options.kinds:
            return frozenset({self.ssh_link(), self.http_link(playlist_options.relative), self.effective_path(playlist_options.relative)})

        if 'local-ssh' in playlist_options.kinds and self.ipv4 == get_public_ip():
            paths.append(self.ssh_link())
        if 'remote-ssh' in playlist_options.kinds and self.ipv4 != get_public_ip():
            paths.append(self.ssh_link())

        if 'local-http' in playlist_options.kinds and self.ipv4 == get_public_ip():
            paths.append(self.http_link(playlist_options.relative))
        if 'remote-http' in playlist_options.kinds and self.ipv4 != get_public_ip():
            paths.append(self.http_link(playlist_options.relative))

        if 'local' in playlist_options.kinds and os.path.isfile(self.path):
            paths.append(self.effective_path(playlist_options.relative))
        if 'remote' in playlist_options.kinds and not os.path.isfile(self.path):
            paths.append(self.effective_path(playlist_options.relative))
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

    def links(self, playlist_options: PlaylistOptions | None = None) -> frozenset[str]:
        playlist_options = playlist_options if playlist_options is not None else PlaylistOptions()
        return frozenset(itertools.chain(*[folder.links(playlist_options) for folder in self.folders]))

    @property
    def slug(self) -> str:
        '''Slugify music'''
        return slugify(
            f"""{self.artist}-{self.title}""",
            stopwords=STOPWORDS,
            replacements=REPLACEMENTS,
        )
