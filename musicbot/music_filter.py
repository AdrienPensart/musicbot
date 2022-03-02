import json
import logging
from typing import Any, Optional

import attr

logger = logging.getLogger(__name__)

DEFAULT_SFTP = False
DEFAULT_HTTP = False
DEFAULT_LOCAL = True
DEFAULT_SPOTIFY = False
DEFAULT_YOUTUBE = False
RATING_CHOICES: list[float] = [x * 0.5 for x in range(0, 11)]
MIN_INT = 0
MAX_INT = 2147483647
DEFAULT_NAME: Optional[str] = None
DEFAULT_RELATIVE = False
DEFAULT_SHUFFLE = False
DEFAULT_GENRES: list[str] = []
DEFAULT_NO_GENRES: list[str] = []
DEFAULT_LIMIT = MAX_INT
DEFAULT_MIN_LENGTH = MIN_INT
DEFAULT_MAX_LENGTH = MAX_INT
DEFAULT_MIN_SIZE = MIN_INT
DEFAULT_MAX_SIZE = MAX_INT
DEFAULT_MIN_RATING = min(RATING_CHOICES)
DEFAULT_MAX_RATING = max(RATING_CHOICES)
DEFAULT_KEYWORDS: list[str] = []
DEFAULT_NO_KEYWORDS: list[str] = []
DEFAULT_ARTISTS: list[str] = []
DEFAULT_NO_ARTISTS: list[str] = []
DEFAULT_TITLES: list[str] = []
DEFAULT_NO_TITLES: list[str] = []
DEFAULT_ALBUMS: list[str] = []
DEFAULT_NO_ALBUMS: list[str] = []


@attr.s(auto_attribs=True, frozen=True)
class MusicFilter:
    name: Optional[str] = DEFAULT_NAME
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
    genres: list[str] = DEFAULT_GENRES
    no_genres: list[str] = DEFAULT_NO_GENRES
    keywords: list[str] = DEFAULT_KEYWORDS
    no_keywords: list[str] = DEFAULT_NO_KEYWORDS
    artists: list[str] = DEFAULT_ARTISTS
    no_artists: list[str] = DEFAULT_NO_ARTISTS
    titles: list[str] = DEFAULT_TITLES
    no_titles: list[str] = DEFAULT_NO_TITLES
    albums: list[str] = DEFAULT_ALBUMS
    no_albums: list[str] = DEFAULT_NO_ALBUMS

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

        is_bad_artists = set(self.artists).intersection(self.no_artists)
        is_bad_genres = set(self.genres).intersection(self.no_genres)
        is_bad_albums = set(self.albums).intersection(self.no_albums)
        is_bad_titles = set(self.titles).intersection(self.no_titles)
        is_bad_keywords = set(self.keywords).intersection(self.no_keywords)
        not_empty_set = is_bad_artists or is_bad_genres or is_bad_albums or is_bad_titles or is_bad_keywords
        if not_empty_set:
            raise ValueError(f"You can't have duplicates value in filters {self}")
        logger.debug(f'Filter: {self}')

    def __repr__(self) -> str:
        return json.dumps(attr.asdict(self))

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
    MusicFilter(name="no artist set", artists=[""]),
    MusicFilter(name="no album set", albums=[""]),
    MusicFilter(name="no title set", titles=[""]),
    MusicFilter(name="no genre set", genres=[""]),
    MusicFilter(name="no rating", min_rating=0.0, max_rating=0.0),
    MusicFilter(name="best (4.0+)", min_rating=4.0, no_keywords=["cutoff", "bad", "demo", "intro"]),
    MusicFilter(name="best (4.5+)", min_rating=4.5, no_keywords=["cutoff", "bad", "demo", "intro"]),
    MusicFilter(name="best (5.0+)", min_rating=5.0, no_keywords=["cutoff", "bad", "demo", "intro"]),
    MusicFilter(name="no live", no_keywords=["live"]),
    MusicFilter(name="only live", keywords=["live"]),
]
