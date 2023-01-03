import logging
from pathlib import Path

from beartype import beartype
from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
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

    @beartype
    def on_modified(self, event: FileModifiedEvent) -> None:
        _ = self.update_music(event.src_path)

    @beartype
    def on_created(self, event: FileCreatedEvent) -> None:
        _ = self.update_music(event.src_path)

    @beartype
    def on_deleted(self, event: FileDeletedEvent) -> None:
        logger.debug(f'Deleting entry in DB for: {event.src_path} {event.event_type}')
        self.musicdb.sync_remove_music_path(event.src_path)

    @beartype
    def on_moved(self, event: FileMovedEvent) -> None:
        logger.debug(f'Moving entry in DB for: {event.src_path} {event.event_type}')
        self.musicdb.sync_remove_music_path(event.src_path)
        _ = self.update_music(event.dest_path)

    @beartype
    def update_music(self, path: str) -> File | None:
        for directory in self.folders.directories:
            if path.startswith(str(directory)) and path.endswith(tuple(self.folders.extensions)):
                MusicbotObject.success(f'{path} : updated')
                return self.musicdb.sync_upsert_path((directory, Path(path)))
        return None
