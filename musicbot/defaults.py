from typing import Final

MIN_INT: Final[int] = 0
MAX_INT: Final[int] = 2147483647

RATING_CHOICES: Final[list[float]] = [x * 0.5 for x in range(0, 11)]
STORED_RATING_CHOICES: Final[list[float]] = [float(x) / 10.0 for x in range(0, 11)]
DEFAULT_RATINGS: Final[list[float]] = [4.0, 4.5, 5.0]
DEFAULT_NAME: Final[str | None] = None
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

DEFAULT_SPOTIFY_USERNAME: Final[str | None] = None
DEFAULT_SPOTIFY_CLIENT_ID: Final[str | None] = None
DEFAULT_SPOTIFY_CLIENT_SECRET: Final[str | None] = None
DEFAULT_SPOTIFY_TOKEN: str | None = None
DEFAULT_SPOTIFY_CACHE_PATH = '~/.spotify_cache'
DEFAULT_SPOTIFY_SCOPE = 'user-library-read,user-library-modify,user-follow-read,user-top-read,user-modify-playback-state,user-read-currently-playing,user-read-playback-state,playlist-modify-public,playlist-read-private,playlist-modify-private'
DEFAULT_SPOTIFY_REDIRECT_URI = 'http://localhost:8888/spotify/callback'

DEFAULT_ACOUSTID_API_KEY: Final[str | None] = None
DEFAULT_THREADS: Final[int] = 8
DEFAULT_CLEAN: Final[bool] = False
DEFAULT_DRY: Final[bool] = False
DEFAULT_YES: Final[bool] = False
DEFAULT_SAVE: Final[bool] = False
DEFAULT_OUTPUT: Final[str] = 'table'
DEFAULT_FLAT: Final[bool] = False
DEFAULT_EXTENSIONS: Final[set[str]] = {"mp3", "flac"}
EXCEPT_DIRECTORIES: Final[set[str]] = {'.Spotlight-V100', '.zfs', 'Android', 'LOST.DIR'}

STOPWORDS: Final[list[str]] = [
    'the',
    'remaster',
    'standard',
    'remastered',
    'bonus',
    'cut',
    'part',
    'edition',
    'version',
    'mix',
    'deluxe',
    'edit',
    'album',
    'lp',
    'ep',
    'uk',
    'track',
    'expanded',
    'single',
    'volume',
    'vol',
    'legacy',
    'special',
] + list(map(str, range(1900, 2020)))

REPLACEMENTS: Final[list[list[str]]] = [
    ['praxis', 'buckethead'],
    ['lawson-rollins', 'buckethead'],
]

DEFAULT_CHECKS: Final[list[str]] = [
    'no-title',
    'no-artist',
    'no-album',
    'no-genre',
    'no-rating',
    'no-track',
    'invalid-title',
    'invalid-comment',
    'invalid-path',
]
