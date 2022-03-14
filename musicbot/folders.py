import logging
import os
from functools import cached_property
from pathlib import Path
from typing import Callable, Any, Iterator

from attr import define
from musicbot.defaults import (
    DEFAULT_EXTENSIONS,
    EXCEPT_DIRECTORIES
)
from musicbot.file import File
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@define(repr=False, hash=True)
class Folders(MusicbotObject):
    paths: list[Path]
    extensions: set[str] = DEFAULT_EXTENSIONS
    except_directories: set[str] = EXCEPT_DIRECTORIES
    other_files: set[Path] = set()
    limit: int | None = None

    def __attrs_post_init__(self) -> None:
        self.paths = [folder.resolve() for folder in self.paths]

    def apply(self, worker: Callable, **kwargs: Any) -> Any:
        return self.parallel(
            worker,
            list(self.files)[:self.limit],
            **kwargs,
        )

    @property
    def unique_folders(self) -> str:
        return ','.join({str(folder) for folder in self.paths})

    @cached_property
    def musics(self) -> list[File]:
        def worker(path: Path) -> File | None:
            try:
                return File.from_path(path=path)
            except OSError as e:
                logger.error(e)
            return None
        return self.apply(worker, prefix="Loading musics")

    @cached_property
    def files(self) -> set[Path]:
        _files = set()
        for folder in self.paths:
            for root, _, basenames in os.walk(folder):
                if any(e in root for e in self.except_directories):
                    continue
                for basename in basenames:
                    path = Path(folder) / root / basename
                    if not basename.endswith(tuple(self.extensions)):
                        self.other_files.add(path)
                    else:
                        _files.add(path)
        return _files

    def __repr__(self) -> str:
        return ' '.join(str(folder) for folder in self.paths)

    def empty_dirs(self, recursive: bool = True) -> Iterator[str]:
        for root_dir in self.paths:
            dirs_list = []
            for root, dirs, files in os.walk(root_dir, topdown=False):
                if recursive:
                    all_subs_empty = True
                    for sub in dirs:
                        full_sub = os.path.join(root, sub)
                        if full_sub not in dirs_list:
                            all_subs_empty = False
                            break
                else:
                    all_subs_empty = (not dirs)
                if all_subs_empty and not files:
                    dirs_list.append(root)
                    yield root
