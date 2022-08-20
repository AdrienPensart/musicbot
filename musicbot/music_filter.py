import json
import logging

from attr import asdict, frozen

from musicbot.defaults import (
    DEFAULT_LIMIT,
    DEFAULT_MAX_LENGTH,
    DEFAULT_MAX_RATING,
    DEFAULT_MAX_SIZE,
    DEFAULT_MIN_LENGTH,
    DEFAULT_MIN_RATING,
    DEFAULT_MIN_SIZE,
    MATCH_ALL,
    RATING_CHOICES
)

logger = logging.getLogger(__name__)


@frozen(repr=False)
class MusicFilter:
    min_size: int = DEFAULT_MIN_SIZE
    max_size: int = DEFAULT_MAX_SIZE
    min_length: int = DEFAULT_MIN_LENGTH
    max_length: int = DEFAULT_MAX_LENGTH
    min_rating: float = DEFAULT_MIN_RATING
    max_rating: float = DEFAULT_MAX_RATING
    limit: int = DEFAULT_LIMIT

    genre: str = MATCH_ALL
    keyword: str = MATCH_ALL
    artist: str = MATCH_ALL
    title: str = MATCH_ALL
    album: str = MATCH_ALL

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

    def __repr__(self) -> str:
        return json.dumps(asdict(self))


NO_KEYWORD = '^((?!cutoff|bad|demo|intro).)$'

DEFAULT_PRE_FILTERS = {
    'to-fix': MusicFilter(keyword="(tofix|todo|spotify-error)"),
    'no-artist': MusicFilter(artist="^$"),
    'no-album': MusicFilter(album="^$"),
    'no-title': MusicFilter(title="^$"),
    'no-genre': MusicFilter(genre="^$"),
    'no-keyword': MusicFilter(keyword="^$"),
    'no-rating': MusicFilter(min_rating=0.0, max_rating=0.0),
    'bests-4.0': MusicFilter(min_rating=4.0, keyword=NO_KEYWORD),
    'bests-4.5': MusicFilter(min_rating=4.5, keyword=NO_KEYWORD),
    'bests-5.0': MusicFilter(min_rating=5.0, keyword=NO_KEYWORD),
}
