from warnings import filterwarnings

from musicbot.config import Config
from musicbot.file import File, Issue
from musicbot.folder import Folder
from musicbot.helpers import syncify
from musicbot.music import Music, MusicInput
from musicbot.music_filter import MusicFilter
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.playlist_options import PlaylistOptions
from musicbot.scan_folders import ScanFolders
from musicbot.spotify import Spotify

filterwarnings(action="ignore", module=".*vlc.*", category=DeprecationWarning)

__all__ = [
    "MusicbotObject",
    "Issue",
    "Config",
    "File",
    "Music",
    "MusicInput",
    "MusicFilter",
    "Playlist",
    "PlaylistOptions",
    "MusicDb",
    "Folder",
    "ScanFolders",
    "Spotify",
    "syncify",
]
