MATCH_ALL = "(.*?)"
MIN_INT: int = 0
MAX_INT: int = 2147483647

# DEFAULT_VLC_PARAMS: str = "--vout=dummy --aout=pulse"

KINDS_CHOICES: frozenset[str] = frozenset(["local", "remote", "remote-ssh", "local-ssh", "local-http", "remote-http", "all"])
DEFAULT_KINDS: frozenset[str] = frozenset(["local"])

DEFAULT_RELATIVE: bool = False
DEFAULT_SHUFFLE: bool = False
DEFAULT_INTERLEAVE: bool = False
DEFAULT_MINIMUM_PLAYLIST_SIZE: int = 1

RATING_CHOICES: list[float] = [x * 0.5 for x in range(0, 11)]
STORED_RATING_CHOICES: list[float] = [float(x) / 10.0 for x in range(0, 11)]
DEFAULT_LIMIT: int = MAX_INT
DEFAULT_MIN_LENGTH: int = MIN_INT
DEFAULT_MAX_LENGTH: int = MAX_INT
DEFAULT_MIN_SIZE: int = MIN_INT
DEFAULT_MAX_SIZE: int = MAX_INT
DEFAULT_MIN_RATING: float = min(RATING_CHOICES)
DEFAULT_MAX_RATING: float = max(RATING_CHOICES)

DEFAULT_SPOTIFY_TIMEOUT: int = 10
DEFAULT_SPOTIFY_USERNAME: str | None = None
DEFAULT_SPOTIFY_CLIENT_ID: str | None = None
DEFAULT_SPOTIFY_CLIENT_SECRET: str | None = None
DEFAULT_SPOTIFY_TOKEN: str | None = None
DEFAULT_SPOTIFY_CACHE_PATH = "~/.spotify_cache"
DEFAULT_SPOTIFY_SCOPE = "user-library-read,user-library-modify,user-follow-read,user-top-read,user-modify-playback-state,user-read-currently-playing,user-read-playback-state,playlist-modify-public,playlist-read-private,playlist-modify-private"
DEFAULT_SPOTIFY_REDIRECT_URI = "http://localhost:8888/spotify/callback"
DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST: str = "To Download"

DEFAULT_ACOUSTID_API_KEY: str | None = None
DEFAULT_THREADS: int = 8
DEFAULT_COROUTINES: int = 64
DEFAULT_CLEAN: bool = False
DEFAULT_DRY: bool = False
DEFAULT_YES: bool = False
DEFAULT_SAVE: bool = False
DEFAULT_OUTPUT: str = "table"
DEFAULT_FLAT: bool = False
DEFAULT_EXTENSIONS: frozenset[str] = frozenset({"mp3", "flac"})
EXCEPT_DIRECTORIES: frozenset[str] = frozenset({".Spotlight-V100", ".zfs", "Android", "LOST.DIR"})

STOPWORDS: list[str] = [
    "the",
    "remaster",
    "standard",
    "remastered",
    "bonus",
    "cut",
    "part",
    "edition",
    "feat",
    "featuring",
    "version",
    "mix",
    "deluxe",
    "edit",
    "album",
    "lp",
    "ep",
    "uk",
    "track",
    "expanded",
    "single",
    "volume",
    "vol",
    "legacy",
    "special",
] + list(map(str, range(1900, 2020)))

REPLACEMENTS: list[list[str]] = [
    ["praxis", "buckethead"],
    ["lawson-rollins", "buckethead"],
    ["-M-", "M"],
]
