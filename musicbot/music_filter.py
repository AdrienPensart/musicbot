import json
import logging

from attr import asdict, frozen

from musicbot.defaults import (
    DEFAULT_ALBUMS,
    DEFAULT_ARTISTS,
    DEFAULT_GENRES,
    DEFAULT_KEYWORDS,
    DEFAULT_LIMIT,
    DEFAULT_MAX_LENGTH,
    DEFAULT_MAX_RATING,
    DEFAULT_MAX_SIZE,
    DEFAULT_MIN_LENGTH,
    DEFAULT_MIN_RATING,
    DEFAULT_MIN_SIZE,
    DEFAULT_NAME,
    DEFAULT_NO_ALBUMS,
    DEFAULT_NO_ARTISTS,
    DEFAULT_NO_GENRES,
    DEFAULT_NO_KEYWORDS,
    DEFAULT_NO_TITLES,
    DEFAULT_SHUFFLE,
    DEFAULT_TITLES,
    RATING_CHOICES
)

logger = logging.getLogger(__name__)


@frozen(repr=False)
class MusicFilter:
    name: str | None = DEFAULT_NAME
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
