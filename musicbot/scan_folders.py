import asyncio
import logging
import os
from dataclasses import dataclass
from functools import cached_property
from itertools import islice
from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Callable, Iterator
from natsort import os_sorted
from yaspin import yaspin

from musicbot.defaults import DEFAULT_EXTENSIONS, EXCEPT_DIRECTORIES
from musicbot.file import File, Issue
from musicbot.music import Music
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@beartype
@dataclass(unsafe_hash=True)
class ScanFolders(MusicbotObject):
    directories: list[Path]
    extensions: frozenset[str] = DEFAULT_EXTENSIONS
    except_directories: frozenset[str] = EXCEPT_DIRECTORIES
    limit: int | None = None

    def __post_init__(self) -> None:
        self.directories = [directory.resolve() for directory in self.directories]

    def apply(self, worker: Callable, **kwargs: Any) -> Any:
        return self.parallel_gather(
            worker,
            list(self.folders_and_paths),
            **kwargs,
        )

    @property
    def unique_directories(self) -> str:
        return ",".join({str(directory) for directory in self.directories})

    @cached_property
    def files(self) -> list[File]:
        def worker(folder_and_path: tuple[Path, Path]) -> File | None:
            try:
                folder, path = folder_and_path
                return File.from_path(folder=folder, path=path)
            except OSError as e:
                logger.error(e)
            return None

        return list(os_sorted(self.apply(worker, desc="Loading musics"), lambda f: f.path))[: self.limit]

    @cached_property
    def musics(self) -> list[Music]:
        return [file.music for file in self.files if file.music is not None]

    @cached_property
    def folders_and_paths(self) -> set[tuple[Path, Path]]:
        _files = set()
        n = 0
        with yaspin(text=f"Loading {n} files", color="yellow") as spinner:
            for folder in self.directories:
                for root, _, basenames in os.walk(folder):
                    if any(e in root for e in self.except_directories):
                        continue
                    for basename in basenames:
                        path = Path(folder) / root / basename
                        if basename.endswith(tuple(self.extensions)):
                            _files.add((folder, path))
                            n += 1
                            spinner.text = f"Loading {n} files"
        return set(islice(_files, self.limit))

    @cached_property
    def paths(self) -> set[Path]:
        return {folder_and_path[1] for folder_and_path in self.folders_and_paths}

    def __repr__(self) -> str:
        return " ".join(str(folder) for folder in self.directories)

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
            except Exception as error:
                self.err(f"{path} : unable to convert to mp3", error=error)
            return None

        return self.apply(
            worker,
            desc="Converting flac to mp3",
            threads=threads,
        )

    def flush_m3u(self) -> None:
        for directory in self.directories:
            for filename in directory.glob("*.m3u"):
                if self.dry:
                    self.success(f"{self} : removing {filename}")
                else:
                    filename.unlink()

    async def scan(self, musicdb: MusicDb) -> list[Music]:
        max_value = len(self.folders_and_paths)
        if not max_value:
            self.warn(f"No music folder or paths discovered from directories {self.directories}")
            return []

        failed_inputs = []
        music_outputs = []
        files = self.files
        with self.progressbar(desc="Upserting musics", max_value=max_value) as pbar:

            async def upsert_worker(file: File) -> None:
                try:
                    issues = file.issues
                    if Issue.NO_TITLE in issues or Issue.NO_ARTIST in issues or Issue.NO_ALBUM in issues:
                        self.warn(f"{file} : missing mandatory fields title/album/artist : {issues}")
                        return
                    if (music_input := file.music_input) is None:
                        self.err(f"{file} : cannot upsert music without physical folder !")
                        return

                    if (music_output := await musicdb.upsert_music(music_input)) is None:
                        self.err(f"{music_input} : unable to insert")
                        failed_inputs.append(file.music_input)
                    else:
                        music_outputs.append(music_output)
                finally:
                    pbar.value += 1
                    _ = pbar.update()

            async with asyncio.TaskGroup() as tg:
                for file in files:
                    _ = tg.create_task(upsert_worker(file))

        if failed_inputs:
            self.warn(f"Unable to insert {len(failed_inputs)} files")
        return music_outputs
