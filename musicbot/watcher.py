import logging
from pathlib import Path

from watchdog.events import (  # type: ignore
    FileSystemEvent,
    PatternMatchingEventHandler
)

from musicbot.file import File
from musicbot.folders import Folders
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


class MusicWatcherHandler(PatternMatchingEventHandler):
    def __init__(self, musicdb: MusicDb, folders: Folders) -> None:
        super().__init__(
            patterns=[f'*.{extension}' for extension in folders.extensions],
            ignore_directories=True,
        )
        self.folders = folders
        self.musicdb = musicdb

    def on_modified(self, event: FileSystemEvent) -> None:
        _ = self.update_music(event.src_path)

    def on_created(self, event: FileSystemEvent) -> None:
        _ = self.update_music(event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        logger.debug(f'Deleting entry in DB for: {event.src_path} {event.event_type}')
        self.musicdb.sync_remove_music_path(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        logger.debug(f'Moving entry in DB for: {event.src_path} {event.event_type}')
        self.musicdb.sync_remove_music_path(event.src_path)
        _ = self.update_music(event.dest_path)

    def update_music(self, path: str) -> File | None:
        for directory in self.folders.directories:
            if path.startswith(str(directory)) and path.endswith(tuple(self.folders.extensions)):
                MusicbotObject.success(f'{path} : updated')
                return self.musicdb.sync_upsert_path((directory, Path(path)))
        return None
