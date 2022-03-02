import logging
from pathlib import Path
from typing import Iterable

import click
from watchdog.events import (  # type: ignore
    FileSystemEvent,
    PatternMatchingEventHandler
)

from musicbot.file import File
from musicbot.musicdb import MusicDb

logger = logging.getLogger(__name__)


class MusicWatcherHandler(PatternMatchingEventHandler):
    def __init__(self, musicdb: MusicDb, folders: Iterable[Path], extensions: Iterable[str]) -> None:
        PatternMatchingEventHandler.__init__(
            self,
            patterns=[f'*.{extension}' for extension in extensions],
            ignore_directories=True,
        )
        self.folders = folders
        self.musicdb = musicdb
        self.extensions = extensions

    def on_modified(self, event: FileSystemEvent) -> None:
        self.update_music(event.src_path)

    def on_created(self, event: FileSystemEvent) -> None:
        self.update_music(event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        logger.debug(f'Deleting entry in DB for: {event.src_path} {event.event_type}')
        self.musicdb.delete_music(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        logger.debug(f'Moving entry in DB for: {event.src_path} {event.event_type}')
        self.musicdb.delete_music(event.src_path)
        self.update_music(event.dest_path)

    def update_music(self, path: str) -> None:
        for folder in self.folders:
            if path.startswith(str(folder)) and path.endswith(tuple(self.extensions)):
                click.echo(f'Creating/modifying DB for: {path}')
                music = File(path=Path(path))
                self.musicdb.upsert_music(music)
                return
