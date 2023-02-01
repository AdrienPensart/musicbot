import logging
import os
from functools import cached_property
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Iterator

from attr import define
from natsort import os_sorted

from musicbot.defaults import DEFAULT_EXTENSIONS, EXCEPT_DIRECTORIES
from musicbot.exceptions import MusicbotError
from musicbot.file import File
from musicbot.music import Music
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@define(repr=False, hash=True)
class Folders(MusicbotObject):
    directories: list[Path]
    extensions: set[str] = set(DEFAULT_EXTENSIONS)
    except_directories: frozenset[str] = EXCEPT_DIRECTORIES
    other_files: set[Path] = set()
    limit: int | None = None

    def __attrs_post_init__(self) -> None:
        self.directories = [directory.resolve() for directory in self.directories]

    def apply(self, worker: Callable, **kwargs: Any) -> Any:
        return self.parallel_gather(
            worker,
            list(self.folders_and_paths),
            **kwargs,
        )

    @property
    def unique_directories(self) -> str:
        return ','.join({str(directory) for directory in self.directories})

    @cached_property
    def files(self) -> list[File]:
        def worker(folder_and_path: tuple[Path, Path]) -> File | None:
            try:
                folder, path = folder_and_path
                return File.from_path(folder=folder, path=path)
            except OSError as e:
                logger.error(e)
            return None
        return list(os_sorted(self.apply(worker, desc="Loading musics"), lambda f: f.path))[:self.limit]

    @cached_property
    def musics(self) -> list[Music]:
        return [file.music for file in self.files if file.music is not None]

    @cached_property
    def folders_and_paths(self) -> set[tuple[Path, Path]]:
        _files = set()
        for folder in self.directories:
            for root, _, basenames in os.walk(folder):
                if any(e in root for e in self.except_directories):
                    continue
                for basename in basenames:
                    path = Path(folder) / root / basename
                    if not basename.endswith(tuple(self.extensions)):
                        self.other_files.add(path)
                    else:
                        _files.add((folder, path))
        return set(islice(_files, self.limit))

    @cached_property
    def paths(self) -> set[Path]:
        return {folder_and_path[1] for folder_and_path in self.folders_and_paths}

    def __repr__(self) -> str:
        return ' '.join(str(folder) for folder in self.directories)

    def flush_empty_directories(self, recursive: bool = True) -> Iterator[str]:
        for root_dir in self.directories:
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
                    all_subs_empty = not dirs
                if all_subs_empty and not files:
                    dirs_list.append(root)
                    yield root

    def flac_to_mp3(
        self,
        destination: Path,
        threads: int,
        flat: bool,
    ) -> list[File]:
        def worker(folder_and_path: tuple[Path, Path]) -> File | None:
            folder, path = folder_and_path
            try:
                if file := File.from_path(folder=folder, path=path):
                    return file.to_mp3(flat=flat, destination=destination)
            except MusicbotError as e:
                self.err(e)
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"{path} : unable to convert to mp3 : {e}")
            return None

        return self.apply(
            worker,
            desc="Converting flac to mp3",
            threads=threads,
        )
