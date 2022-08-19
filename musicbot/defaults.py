from typing import Final

MATCH_ALL = "(.*?)"
# MATCH_ALL = ""
MIN_INT: Final[int] = 0
MAX_INT: Final[int] = 2147483647

DEFAULT_VLC_PARAMS: Final[str] = "--vout=dummy --aout=pulse"

KINDS_CHOICES: Final[frozenset[str]] = frozenset(['local', 'remote', 'remote-ssh', 'local-ssh', 'local-http', 'remote-http', 'all'])
DEFAULT_KINDS: Final[frozenset[str]] = frozenset(['local'])

DEFAULT_NAME: Final[str] = "unnamed"
DEFAULT_RELATIVE: Final[bool] = False
DEFAULT_SHUFFLE: Final[bool] = False
DEFAULT_INTERLEAVE: Final[bool] = False

RATING_CHOICES: Final[list[float]] = [x * 0.5 for x in range(0, 11)]
STORED_RATING_CHOICES: Final[list[float]] = [float(x) / 10.0 for x in range(0, 11)]
DEFAULT_LIMIT: Final[int] = MAX_INT
DEFAULT_MIN_LENGTH: Final[int] = MIN_INT
DEFAULT_MAX_LENGTH: Final[int] = MAX_INT
DEFAULT_MIN_SIZE: Final[int] = MIN_INT
DEFAULT_MAX_SIZE: Final[int] = MAX_INT
DEFAULT_MIN_RATING: Final[float] = min(RATING_CHOICES)
DEFAULT_MAX_RATING: Final[float] = max(RATING_CHOICES)

DEFAULT_SPOTIFY_TIMEOUT: Final[int] = 10
DEFAULT_SPOTIFY_USERNAME: Final[str | None] = None
DEFAULT_SPOTIFY_CLIENT_ID: Final[str | None] = None
DEFAULT_SPOTIFY_CLIENT_SECRET: Final[str | None] = None
DEFAULT_SPOTIFY_TOKEN: str | None = None
DEFAULT_SPOTIFY_CACHE_PATH = '~/.spotify_cache'
DEFAULT_SPOTIFY_SCOPE = 'user-library-read,user-library-modify,user-follow-read,user-top-read,user-modify-playback-state,user-read-currently-playing,user-read-playback-state,playlist-modify-public,playlist-read-private,playlist-modify-private'
DEFAULT_SPOTIFY_REDIRECT_URI = 'http://localhost:8888/spotify/callback'
DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST: Final[str] = "To Download"

DEFAULT_ACOUSTID_API_KEY: Final[str | None] = None
DEFAULT_THREADS: Final[int] = 8
DEFAULT_COROUTINES: Final[int] = 64
DEFAULT_CLEAN: Final[bool] = False
DEFAULT_DRY: Final[bool] = False
DEFAULT_YES: Final[bool] = False
DEFAULT_SAVE: Final[bool] = False
DEFAULT_OUTPUT: Final[str] = 'table'
DEFAULT_FLAT: Final[bool] = False
DEFAULT_EXTENSIONS: Final[frozenset[str]] = frozenset({"mp3", "flac"})
EXCEPT_DIRECTORIES: Final[frozenset[str]] = frozenset({'.Spotlight-V100', '.zfs', 'Android', 'LOST.DIR'})

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

DEFAULT_CHECKS: Final[frozenset[str]] = frozenset({
    'no-title',
    'no-artist',
    'no-album',
    'no-genre',
    'no-rating',
    'no-track',
    'invalid-title',
    'invalid-comment',
    'invalid-path',
})
