import logging
from typing import List, Optional

DEFAULT_DRY = False
DEFAULT_MB_CONCURRENCY = 8
DEFAULT_YES = False
DEFAULT_SAVE = False
DEFAULT_MB_OUTPUT = 'table'
DEFAULT_MB_PLAYLIST_OUTPUT = 'table'
DEFAULT_MB_FLAT = False

DEFAULT_CONFIG = '~/musicbot.ini'
DEFAULT_LOG = ''
DEFAULT_DEBUG = False
DEFAULT_INFO = False
DEFAULT_WARNING = False
DEFAULT_ERROR = False
DEFAULT_CRITICAL = False
DEFAULT_TIMINGS = False
DEFAULT_VERBOSITY = 'warning'
DEFAULT_QUIET = False

VERBOSITIES = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

MB_CONFIG = 'MB_CONFIG'
MB_LOG = 'MB_LOG'
MB_DEBUG = 'MB_DEBUG'
MB_INFO = 'MB_INFO'
MB_WARNING = 'MB_WARNING'
MB_ERROR = 'MB_ERROR'
MB_CRITICAL = 'MB_CRITICAL'
MB_TIMINGS = 'MB_TIMINGS'
MB_VERBOSITY = 'MB_VERBOSITY'
MB_QUIET = 'MB_QUIET'

DEFAULT_EMAIL: Optional[str] = None
DEFAULT_PASSWORD: Optional[str] = None
DEFAULT_FIRST_NAME: Optional[str] = None
DEFAULT_LAST_NAME: Optional[str] = None
DEFAULT_TOKEN: Optional[str] = None
DEFAULT_GRAPHQL = 'http://127.0.0.1:5000/graphql'

DEFAULT_GRAPHQL_ADMIN = 'http://127.0.0.1:5001/graphql'
DEFAULT_GRAPHQL_ADMIN_USER: Optional[str] = None
DEFAULT_GRAPHQL_ADMIN_PASSWORD: Optional[str] = None

DEFAULT_SPOTIFY_USERNAME: Optional[str] = None
DEFAULT_SPOTIFY_CLIENT_ID: Optional[str] = None
DEFAULT_SPOTIFY_CLIENT_SECRET: Optional[str] = None
DEFAULT_SPOTIFY_TOKEN: Optional[str] = None
DEFAULT_SPOTIFY_CACHE_PATH = '~/.spotify_cache'
DEFAULT_SPOTIFY_SCOPE = 'user-library-read,user-follow-read,user-top-read,playlist-read-private,user-modify-playback-state,user-read-currently-playing,user-read-playback-state'
DEFAULT_SPOTIFY_REDIRECT_URI = 'http://localhost:8888/spotify/callback'

DEFAULT_ACOUSTID_API_KEY: Optional[str] = None

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
