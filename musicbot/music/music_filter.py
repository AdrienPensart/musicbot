import logging
import json
from typing import Any, Dict, List, Optional
import attr
from musicbot.helpers import parse_graphql

logger = logging.getLogger(__name__)

RATING_CHOICES: List[float] = [x * 0.5 for x in range(0, 11)]
MIN_INT = 0
MAX_INT = 2147483647
DEFAULT_NAME: Optional[str] = None
DEFAULT_RELATIVE = False
DEFAULT_SHUFFLE = False
DEFAULT_GENRES: List[str] = []
DEFAULT_NO_GENRES: List[str] = []
DEFAULT_LIMIT = MAX_INT
DEFAULT_MIN_DURATION = MIN_INT
DEFAULT_MAX_DURATION = MAX_INT
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
    shuffle: bool = DEFAULT_SHUFFLE
    min_duration: int = DEFAULT_MIN_DURATION
    max_duration: int = DEFAULT_MAX_DURATION
    min_rating: float = DEFAULT_MIN_RATING
    max_rating: float = DEFAULT_MAX_RATING
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
        if self.min_rating not in RATING_CHOICES:
            raise ValueError(f"Invalid minimum rating {self.min_rating}, it should be one of {RATING_CHOICES}")

        if self.max_rating not in RATING_CHOICES:
            raise ValueError(f"Invalid maximum rating {self.max_rating}, it should be one of {RATING_CHOICES}")

        if self.min_rating > self.max_rating:
            raise ValueError(f"Invalid minimum ({self.min_rating}) or maximum ({self.max_rating}) rating")

        if self.min_duration > self.max_duration:
            raise ValueError(f"Invalid minimum ({self.min_duration}) or maximum ({self.max_duration}) duration")

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

    def upsert_mutation(self, user_id: str, operation=None) -> str:
        operation = operation if operation is not None else ""
        mutation = f'''
        mutation {operation} {{
            upsertFilter(
                where: {{
                    name: "{self.name}"
                    userId: {user_id}
                }}
                input: {{
                    filter: {{
                        name: "{self.name}",
                        minDuration: {self.min_duration},
                        maxDuration: {self.max_duration},
                        minRating: {self.min_rating},
                        maxRating: {self.max_rating},
                        artists: {json.dumps(self.artists)},
                        noArtists: {json.dumps(self.no_artists)},
                        albums: {json.dumps(self.albums)},
                        noAlbums: {json.dumps(self.no_albums)},
                        titles: {json.dumps(self.titles)},
                        noTitles: {json.dumps(self.no_titles)},
                        genres: {json.dumps(self.genres)},
                        noGenres: {json.dumps(self.no_genres)},
                        keywords: {json.dumps(self.keywords)},
                        noKeywords: {json.dumps(self.no_keywords)},
                        shuffle: {json.dumps(self.shuffle)},
                        limit: {self.limit},
                    }}
                }}
            )
            {{
                clientMutationId
            }}
        }}
        '''
        parse_graphql(mutation)
        return mutation

    def as_dict(self) -> Dict[str, Any]:  # pylint: disable=unsubscriptable-object
        return {
            'minDuration': self.min_duration,
            'maxDuration': self.max_duration,
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
            'keywords': self.keywords,
            'noKeywords': self.no_keywords,
            'shuffle': self.shuffle,
            'limit': self.limit,
        }

    def to_graphql(self) -> str:
        return ", ".join([f'{k}: {json.dumps(v)}' for k, v in self.as_dict().items()])


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
