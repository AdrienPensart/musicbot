from warnings import filterwarnings

from musicbot.config import Config
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist

filterwarnings(action="ignore", module=".*vlc.*", category=DeprecationWarning)

__all__ = [
    "MusicbotObject",
    "Config",
    "File",
    "Music",
    "MusicFilter",
    "Playlist",
    "MusicDb",
    "Folders",
]
