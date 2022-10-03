import logging
from typing import Any

from attr import asdict, field, fields, frozen

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
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@frozen(repr=False)
class MusicFilter(MusicbotObject):
    genre: str = field(default=MATCH_ALL)
    keyword: str = field(default=MATCH_ALL)
    artist: str = field(default=MATCH_ALL)
    title: str = field(default=MATCH_ALL)
    album: str = field(default=MATCH_ALL)

    min_size = field(converter=int, default=DEFAULT_MIN_SIZE)
    max_size = field(converter=int, default=DEFAULT_MAX_SIZE)
    min_length = field(converter=int, default=DEFAULT_MIN_LENGTH)
    max_length = field(converter=int, default=DEFAULT_MAX_LENGTH)
    min_rating = field(converter=float, default=DEFAULT_MIN_RATING)
    max_rating = field(converter=float, default=DEFAULT_MAX_RATING)
    limit = field(converter=int, default=DEFAULT_LIMIT)

    @min_rating.validator
    def _check_min_rating(self, attribute: Any, value: float) -> None:  # pylint: disable=unused-argument
        '''min rating validator'''
        if value not in RATING_CHOICES:
            raise ValueError(f"Invalid minimum rating {self.min_rating}, it should be one of {RATING_CHOICES}")

    @max_rating.validator
    def _check_max_rating(self, attribute: Any, value: float) -> None:  # pylint: disable=unused-argument
        '''max rating validator'''
        if value not in RATING_CHOICES:
            raise ValueError(f"Invalid maximum rating {self.max_rating}, it should be one of {RATING_CHOICES}")

        if self.min_rating > value:
            raise ValueError(f"Invalid minimum ({self.min_rating}) or maximum ({self.max_rating}) rating")

    @max_length.validator
    def _check_max_length(self, attribute: Any, value: int) -> None:  # pylint: disable=unused-argument
        '''max length validator'''
        if self.min_length > value:
            raise ValueError(f"Invalid minimum ({self.min_length}) or maximum ({self.max_length}) length")

    @max_size.validator
    def _check_max_size(self, attribute: Any, value: int) -> None:  # pylint: disable=unused-argument
        '''max size validator'''
        if self.min_size > value:
            raise ValueError(f"Invalid minimum ({self.min_size}) or maximum ({self.max_size}) size")

    def __repr__(self) -> str:
        self_dict = asdict(self)
        for field_attribute in fields(MusicFilter):  # pylint: disable=not-an-iterable
            if self_dict[field_attribute.name] == field_attribute.default:
                del self_dict[field_attribute.name]
        representation = self.dumps_json(self_dict)
        if representation is not None:
            return representation
        self.err(f'Unable to convert to json : {self_dict}')
        return '{}'


NO_KEYWORD = '^((?!cutoff|bad|demo|intro).)$'

DEFAULT_PREFILTERS = {
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
