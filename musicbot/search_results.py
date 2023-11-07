import logging
from dataclasses import dataclass

import edgedb
from beartype import beartype

from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@beartype
@dataclass(frozen=True)
class SearchResults(MusicbotObject):
    musics: list[edgedb.Object]
    artists: list[edgedb.Object]
    albums: list[edgedb.Object]
    genres: list[edgedb.Object]
    keywords: list[edgedb.Object]
