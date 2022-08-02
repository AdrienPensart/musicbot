import logging

import yaml
from attr import asdict, frozen
from slugify import slugify

from musicbot.defaults import REPLACEMENTS, STOPWORDS
from musicbot.helpers import bytes_to_human, precise_seconds_to_human
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


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
    keywords: set[str]
    links: set[str]

    def human_repr(self) -> str:
        d = asdict(self)
        d['links'] = [link.removeprefix('sftp://') for link in d['links']]
        d['size'] = bytes_to_human(d['size'])
        d['length'] = precise_seconds_to_human(d['length'])
        return yaml.dump(d, sort_keys=False)

    # def sftp_links(self):
    #     for link in links:

    @property
    def slug(self) -> str:
        '''Slugify music'''
        return slugify(f"""{self.artist}-{self.title}""", stopwords=STOPWORDS, replacements=REPLACEMENTS)
