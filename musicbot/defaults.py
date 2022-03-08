from typing import Final

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
DEFAULT_EXTENSIONS: Final[list[str]] = ["mp3", "flac"]
EXCEPT_DIRECTORIES: Final[list[str]] = ['.Spotlight-V100', '.zfs', 'Android', 'LOST.DIR']
RATING_CHOICES: Final[list[float]] = [x * 0.5 for x in range(0, 11)]
MIN_INT: Final[int] = 0
MAX_INT: Final[int] = 2147483647

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
