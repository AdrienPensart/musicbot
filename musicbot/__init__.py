from warnings import filterwarnings

from musicbot.config import Config
from musicbot.file import File
from musicbot.folder import Folder
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.playlist_options import PlaylistOptions
from musicbot.scan_folders import ScanFolders
from musicbot.search_results import SearchResults
from musicbot.spotify import Spotify
from musicbot.helpers import syncify

filterwarnings(action="ignore", module=".*vlc.*", category=DeprecationWarning)

__all__ = [
    "MusicbotObject",
    "Config",
    "File",
    "Music",
    "MusicFilter",
    "Playlist",
    "PlaylistOptions",
    "MusicDb",
    "Folder",
    "ScanFolders",
    "SearchResults",
    "Spotify",
    "syncify",
]
