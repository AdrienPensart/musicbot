import logging
import json
from typing import Any, Dict, List, Optional
import attr

logger = logging.getLogger(__name__)

RATING_CHOICES: List[float] = [x * 0.5 for x in range(0, 11)]
MIN_INT = 0
MAX_INT = 2147483647
DEFAULT_NAME: Optional[str] = None
DEFAULT_RELATIVE = False
DEFAULT_SHUFFLE = False
DEFAULT_YOUTUBES: List[str] = []
DEFAULT_NO_YOUTUBES: List[str] = []
DEFAULT_SPOTIFYS: List[str] = []
DEFAULT_NO_SPOTIFYS: List[str] = []
DEFAULT_FORMATS: List[str] = []
DEFAULT_NO_FORMATS: List[str] = []
DEFAULT_GENRES: List[str] = []
DEFAULT_NO_GENRES: List[str] = []
DEFAULT_LIMIT = MAX_INT
DEFAULT_MIN_DURATION = MIN_INT
DEFAULT_MAX_DURATION = MAX_INT
DEFAULT_MIN_SIZE = MIN_INT
DEFAULT_MAX_SIZE = MAX_INT
DEFAULT_MIN_RATING = min(RATING_CHOICES)
DEFAULT_MAX_RATING = max(RATING_CHOICES)
DEFAULT_KEYWORDS: List[str] = []
DEFAULT_NO_KEYWORDS: List[str] = []
DEFAULT_ARTISTS: List[str] = []
DEFAULT_NO_ARTISTS: List[str] = []
DEFAULT_TITLES: List[str] = []
DEFAULT_NO_TITLES: List[str] = []
DEFAULT_ALBUMS: List[str] = []
DEFAULT_NO_ALBUMS: List[str] = []


@attr.s(auto_attribs=True, frozen=True)
class MusicFilter:
    name: Optional[str] = DEFAULT_NAME
    relative: bool = DEFAULT_RELATIVE
    shuffle: bool = DEFAULT_SHUFFLE
    min_duration: int = DEFAULT_MIN_DURATION
    max_duration: int = DEFAULT_MAX_DURATION
    min_size: int = DEFAULT_MIN_SIZE
    max_size: int = DEFAULT_MIN_SIZE
    min_rating: float = DEFAULT_MIN_RATING
    max_rating: float = DEFAULT_MAX_RATING
    youtubes: List[str] = DEFAULT_YOUTUBES
    no_youtubes: List[str] = DEFAULT_NO_YOUTUBES
    spotifys: List[str] = DEFAULT_SPOTIFYS
    no_spotifys: List[str] = DEFAULT_NO_SPOTIFYS
    formats: List[str] = DEFAULT_FORMATS
    no_formats: List[str] = DEFAULT_NO_FORMATS
    limit: int = DEFAULT_LIMIT
    genres: List[str] = DEFAULT_GENRES
    no_genres: List[str] = DEFAULT_NO_GENRES
    keywords: List[str] = DEFAULT_KEYWORDS
    no_keywords: List[str] = DEFAULT_NO_KEYWORDS
    artists: List[str] = DEFAULT_ARTISTS
    no_artists: List[str] = DEFAULT_NO_ARTISTS
    titles: List[str] = DEFAULT_TITLES
    no_titles: List[str] = DEFAULT_NO_TITLES
    albums: List[str] = DEFAULT_ALBUMS
    no_albums: List[str] = DEFAULT_NO_ALBUMS

    def __attrs_post_init__(self) -> None:
        if self.min_size > self.max_size:
            raise ValueError(f"Invalid minimum ({self.min_rating}) or maximum ({self.max_rating}) size")

        if self.min_rating not in RATING_CHOICES:
            raise ValueError(f"Invalid minimum rating {self.min_rating}, it should be one of {RATING_CHOICES}")

        if self.max_rating not in RATING_CHOICES:
            raise ValueError(f"Invalid maximum rating {self.max_rating}, it should be one of {RATING_CHOICES}")

        if self.min_rating > self.max_rating:
            raise ValueError(f"Invalid minimum ({self.min_rating}) or maximum ({self.max_rating}) rating")

        if self.min_duration > self.max_duration:
            raise ValueError(f"Invalid minimum ({self.min_duration}) or maximum ({self.max_duration}) duration")

        is_bad_formats = set(self.formats).intersection(self.no_formats)
        is_bad_artists = set(self.artists).intersection(self.no_artists)
        is_bad_genres = set(self.genres).intersection(self.no_genres)
        is_bad_albums = set(self.albums).intersection(self.no_albums)
        is_bad_titles = set(self.titles).intersection(self.no_titles)
        is_bad_keywords = set(self.keywords).intersection(self.no_keywords)
        not_empty_set = is_bad_formats or is_bad_artists or is_bad_genres or is_bad_albums or is_bad_titles or is_bad_keywords
        if not_empty_set:
            raise ValueError(f"You can't have duplicates value in filters {self}")
        logger.debug(f'Filter: {self}')

    def __repr__(self) -> str:
        return json.dumps(self.as_dict())

    def diff(self) -> Dict[str, Any]:
        '''Print only differences with default filter'''
        myself = vars(self)
        default = vars(MusicFilter())
        return {k: myself[k] for k in myself if default[k] != myself[k] and k != 'name'}

    def common(self) -> Dict[str, Any]:
        '''Print common values with default filter'''
        myself = vars(self)
        default = vars(MusicFilter())
        return {k: myself[k] for k in myself if default[k] == myself[k] and k != 'name'}

    def as_dict(self) -> Dict[str, Any]:  # pylint: disable=unsubscriptable-object
        return {
            'minDuration': self.min_duration,
            'maxDuration': self.max_duration,
            'minSize': self.min_size,
            'maxSize': self.max_size,
            'minRating': self.min_rating,
            'maxRating': self.max_rating,
            'artists': self.artists,
            'noArtists': self.no_artists,
            'albums': self.albums,
            'noAlbums': self.no_albums,
            'titles': self.titles,
            'noTitles': self.no_titles,
            'genres': self.genres,
            'noGenres': self.no_genres,
            'formats': self.formats,
            'noFormats': self.no_formats,
            'keywords': self.keywords,
            'noKeywords': self.no_keywords,
            'shuffle': self.shuffle,
            'relative': self.relative,
            'limit': self.limit,
            'youtubes': self.youtubes,
            'noYoutubes': self.no_youtubes,
            'spotifys': self.spotifys,
            'noSpotifys': self.no_spotifys,
        }

    def to_graphql(self) -> str:
        return ", ".join([f'{k}: {json.dumps(v)}' for k, v in self.as_dict().items()])
