import json
import logging
from typing import Final, Any

from attr import frozen, asdict
from musicbot.defaults import (
    RATING_CHOICES,
    MIN_INT,
    MAX_INT,
)

logger = logging.getLogger(__name__)

DEFAULT_SFTP: Final[bool] = False
DEFAULT_HTTP: Final[bool] = False
DEFAULT_LOCAL: Final[bool] = True
DEFAULT_SPOTIFY: Final[bool] = False
DEFAULT_YOUTUBE: Final[bool] = False
DEFAULT_NAME: Final[str | None] = None
DEFAULT_RELATIVE: Final[bool] = False
DEFAULT_SHUFFLE: Final[bool] = False
DEFAULT_LIMIT: Final[int] = MAX_INT
DEFAULT_MIN_LENGTH: Final[int] = MIN_INT
DEFAULT_MAX_LENGTH: Final[int] = MAX_INT
DEFAULT_MIN_SIZE: Final[int] = MIN_INT
DEFAULT_MAX_SIZE: Final[int] = MAX_INT
DEFAULT_MIN_RATING: Final[float] = min(RATING_CHOICES)
DEFAULT_MAX_RATING: Final[float] = max(RATING_CHOICES)

DEFAULT_GENRES: Final[frozenset[str]] = frozenset()
DEFAULT_NO_GENRES: Final[frozenset[str]] = frozenset()
DEFAULT_KEYWORDS: Final[frozenset[str]] = frozenset()
DEFAULT_NO_KEYWORDS: Final[frozenset[str]] = frozenset()
DEFAULT_ARTISTS: Final[frozenset[str]] = frozenset()
DEFAULT_NO_ARTISTS: Final[frozenset[str]] = frozenset()
DEFAULT_TITLES: Final[frozenset[str]] = frozenset()
DEFAULT_NO_TITLES: Final[frozenset[str]] = frozenset()
DEFAULT_ALBUMS: Final[frozenset[str]] = frozenset()
DEFAULT_NO_ALBUMS: Final[frozenset[str]] = frozenset()


@frozen
class MusicFilter:
    name: str | None = DEFAULT_NAME
    sftp: bool = DEFAULT_SFTP
    http: bool = DEFAULT_HTTP
    local: bool = DEFAULT_LOCAL
    spotify: bool = DEFAULT_SPOTIFY
    youtube: bool = DEFAULT_YOUTUBE
    shuffle: bool = DEFAULT_SHUFFLE
    min_size: int = DEFAULT_MIN_SIZE
    max_size: int = DEFAULT_MAX_SIZE
    min_length: int = DEFAULT_MIN_LENGTH
    max_length: int = DEFAULT_MAX_LENGTH
    min_rating: float = DEFAULT_MIN_RATING
    max_rating: float = DEFAULT_MAX_RATING
    limit: int = DEFAULT_LIMIT

    genres: frozenset[str] = DEFAULT_GENRES
    no_genres: frozenset[str] = DEFAULT_NO_GENRES
    keywords: frozenset[str] = DEFAULT_KEYWORDS
    no_keywords: frozenset[str] = DEFAULT_NO_KEYWORDS
    artists: frozenset[str] = DEFAULT_ARTISTS
    no_artists: frozenset[str] = DEFAULT_NO_ARTISTS
    titles: frozenset[str] = DEFAULT_TITLES
    no_titles: frozenset[str] = DEFAULT_NO_TITLES
    albums: frozenset[str] = DEFAULT_ALBUMS
    no_albums: frozenset[str] = DEFAULT_NO_ALBUMS

    def __attrs_post_init__(self) -> None:
        if self.min_rating not in RATING_CHOICES:
            raise ValueError(f"Invalid minimum rating {self.min_rating}, it should be one of {RATING_CHOICES}")

        if self.max_rating not in RATING_CHOICES:
            raise ValueError(f"Invalid maximum rating {self.max_rating}, it should be one of {RATING_CHOICES}")

        if self.min_rating > self.max_rating:
            raise ValueError(f"Invalid minimum ({self.min_rating}) or maximum ({self.max_rating}) rating")

        if self.min_length > self.max_length:
            raise ValueError(f"Invalid minimum ({self.min_length}) or maximum ({self.max_length}) length")

        if self.min_size > self.max_size:
            raise ValueError(f"Invalid minimum ({self.min_size}) or maximum ({self.max_size}) size")

        is_bad_artists = self.artists.intersection(self.no_artists)
        is_bad_genres = self.genres.intersection(self.no_genres)
        is_bad_albums = self.albums.intersection(self.no_albums)
        is_bad_titles = self.titles.intersection(self.no_titles)
        is_bad_keywords = self.keywords.intersection(self.no_keywords)
        not_empty_set = is_bad_artists or is_bad_genres or is_bad_albums or is_bad_titles or is_bad_keywords
        if not_empty_set:
            raise ValueError(f"You can't have duplicates value in filters {self}")
        logger.debug(f'Filter: {self}')

    def __repr__(self) -> str:
        return json.dumps(asdict(self))

    def diff(self) -> dict[str, Any]:
        '''Print only differences with default filter'''
        myself = vars(self)
        default = vars(MusicFilter())
        return {k: myself[k] for k in myself if default[k] != myself[k] and k != 'name'}

    def common(self) -> dict[str, Any]:
        '''Print common values with default filter'''
        myself = vars(self)
        default = vars(MusicFilter())
        return {k: myself[k] for k in myself if default[k] == myself[k] and k != 'name'}


default_filters = [
    MusicFilter(name="default"),
    MusicFilter(name="no artist set", artists=frozenset("")),
    MusicFilter(name="no album set", albums=frozenset("")),
    MusicFilter(name="no title set", titles=frozenset("")),
    MusicFilter(name="no genre set", genres=frozenset("")),
    MusicFilter(name="no rating", min_rating=0.0, max_rating=0.0),
    MusicFilter(name="best (4.0+)", min_rating=4.0, no_keywords=frozenset(("cutoff", "bad", "demo", "intro"))),
    MusicFilter(name="best (4.5+)", min_rating=4.5, no_keywords=frozenset(("cutoff", "bad", "demo", "intro"))),
    MusicFilter(name="best (5.0+)", min_rating=5.0, no_keywords=frozenset(("cutoff", "bad", "demo", "intro"))),
    MusicFilter(name="no live", no_keywords=frozenset("live")),
    MusicFilter(name="only live", keywords=frozenset("live")),
]
