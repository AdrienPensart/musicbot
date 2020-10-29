import logging
from typing import Dict, List, Optional
from typing_extensions import Final

DEFAULT_DRY: Final[bool] = False
DEFAULT_MB_CONCURRENCY: Final[int] = 8
DEFAULT_YES: Final[bool] = False
DEFAULT_SAVE: Final[bool] = False
DEFAULT_MB_OUTPUT: Final[str] = 'table'
DEFAULT_MB_PLAYLIST_OUTPUT: Final[str] = 'table'
DEFAULT_MB_FLAT: Final[bool] = False

DEFAULT_CONFIG: Final[str] = '~/musicbot.ini'
DEFAULT_LOG: Final[str] = ''
DEFAULT_DEBUG: Final[bool] = False
DEFAULT_INFO: Final[bool] = False
DEFAULT_WARNING: Final[bool] = False
DEFAULT_ERROR: Final[bool] = False
DEFAULT_CRITICAL: Final[bool] = False
DEFAULT_TIMINGS: Final[bool] = False
DEFAULT_VERBOSITY: Final[str] = 'warning'
DEFAULT_QUIET: Final[bool] = False

VERBOSITIES: Final[Dict[str, int]] = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

MB_CONFIG: Final[str] = 'MB_CONFIG'
MB_LOG: Final[str] = 'MB_LOG'
MB_DEBUG: Final[str] = 'MB_DEBUG'
MB_INFO: Final[str] = 'MB_INFO'
MB_WARNING: Final[str] = 'MB_WARNING'
MB_ERROR: Final[str] = 'MB_ERROR'
MB_CRITICAL: Final[str] = 'MB_CRITICAL'
MB_TIMINGS: Final[str] = 'MB_TIMINGS'
MB_VERBOSITY: Final[str] = 'MB_VERBOSITY'
MB_QUIET: Final[str] = 'MB_QUIET'

DEFAULT_EMAIL: Final[Optional[str]] = None
DEFAULT_PASSWORD: Final[Optional[str]] = None
DEFAULT_FIRST_NAME: Final[Optional[str]] = None
DEFAULT_LAST_NAME: Final[Optional[str]] = None
DEFAULT_TOKEN: Final[Optional[str]] = None
DEFAULT_GRAPHQL: Final[str] = 'http://127.0.0.1:5000/graphql'

DEFAULT_GRAPHQL_ADMIN: Final[str] = 'http://127.0.0.1:5001/graphql'
DEFAULT_GRAPHQL_ADMIN_USER: Final[Optional[str]] = None
DEFAULT_GRAPHQL_ADMIN_PASSWORD: Final[Optional[str]] = None

DEFAULT_SPOTIFY_USERNAME: Final[Optional[str]] = None
DEFAULT_SPOTIFY_CLIENT_ID: Final[Optional[str]] = None
DEFAULT_SPOTIFY_CLIENT_SECRET: Final[Optional[str]] = None
DEFAULT_SPOTIFY_TOKEN: Final[Optional[str]] = None
DEFAULT_SPOTIFY_CACHE_PATH: Final[str] = '~/.spotify_cache'
DEFAULT_SPOTIFY_SCOPE: Final[str] = 'user-library-read,user-follow-read,user-top-read,playlist-read-private,user-modify-playback-state,user-read-currently-playing,user-read-playback-state'
DEFAULT_SPOTIFY_REDIRECT_URI: Final[str] = 'http://localhost:8888/spotify/callback'

DEFAULT_ACOUSTID_API_KEY: Final[Optional[str]] = None

RATING_CHOICES: Final[List[float]] = [x * 0.5 for x in range(0, 11)]
MIN_INT: Final[int] = 0
MAX_INT: Final[int] = 2147483647

DEFAULT_NAME: Final[Optional[str]] = None
DEFAULT_RELATIVE: Final[bool] = False
DEFAULT_SHUFFLE: Final[bool] = False
DEFAULT_YOUTUBES: Final[List[str]] = []
DEFAULT_NO_YOUTUBES: Final[List[str]] = []
DEFAULT_SPOTIFYS: Final[List[str]] = []
DEFAULT_NO_SPOTIFYS: Final[List[str]] = []
DEFAULT_FORMATS: Final[List[str]] = []
DEFAULT_NO_FORMATS: Final[List[str]] = []
DEFAULT_GENRES: Final[List[str]] = []
DEFAULT_NO_GENRES: Final[List[str]] = []
DEFAULT_LIMIT: Final[int] = MAX_INT
DEFAULT_MIN_DURATION: Final[int] = MIN_INT
DEFAULT_MAX_DURATION: Final[int] = MAX_INT
DEFAULT_MIN_SIZE: Final[int] = MIN_INT
DEFAULT_MAX_SIZE: Final[int] = MAX_INT
DEFAULT_MIN_RATING: Final[float] = min(RATING_CHOICES)
DEFAULT_MAX_RATING: Final[float] = max(RATING_CHOICES)
DEFAULT_KEYWORDS: Final[List[str]] = []
DEFAULT_NO_KEYWORDS: Final[List[str]] = []
DEFAULT_ARTISTS: Final[List[str]] = []
DEFAULT_NO_ARTISTS: Final[List[str]] = []
DEFAULT_TITLES: Final[List[str]] = []
DEFAULT_NO_TITLES: Final[List[str]] = []
DEFAULT_ALBUMS: Final[List[str]] = []
DEFAULT_NO_ALBUMS: Final[List[str]] = []
