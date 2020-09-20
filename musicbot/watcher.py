import logging
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler  # type: ignore
from .music import file
from .user import User

logger = logging.getLogger(__name__)


class MusicWatcherHandler(PatternMatchingEventHandler):  # type: ignore
    def __init__(self, user: User) -> None:
        PatternMatchingEventHandler.__init__(
            self,
            patterns=['*.' + f for f in file.supported_formats],
            ignore_directories=True,
        )
        self.user = user

    def on_modified(self, event: FileSystemEvent) -> None:
        self.update_music(event.src_path)

    def on_created(self, event: FileSystemEvent) -> None:
        self.update_music(event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        logger.debug(f'Deleting entry in DB for: {event.src_path} {event.event_type}')
        self.user.delete_music(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        logger.debug(f'Moving entry in DB for: {event.src_path} {event.event_type}')
        self.user.delete_music(event.src_path)
        self.update_music(event.dest_path)

    def update_music(self, path: str) -> None:
        for folder in self.user.folders():
            if path.startswith(folder) and path.endswith(tuple(file.supported_formats)):
                logger.debug(f'Creating/modifying DB for: {path}')
                f = file.File(path, folder)
                self.user.upsert_music(f)
                return
