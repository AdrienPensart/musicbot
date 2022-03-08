import logging
import os
from pathlib import Path
from typing import Iterable, Iterator

from musicbot.defaults import DEFAULT_EXTENSIONS, EXCEPT_DIRECTORIES
from musicbot.file import File
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


class Folders(MusicbotObject):
    def __init__(
        self,
        folders: Iterable[Path],
        extensions: Iterable[str] | None,
        threads: int | None = None,
    ):
        self.supported_formats = extensions if extensions is not None else DEFAULT_EXTENSIONS
        self.folders = [folder.resolve() for folder in folders]
        self.files = []
        self.other_files: list[Path] = []

        for folder in self.folders:
            for root, _, basenames in os.walk(folder):
                if any(e in root for e in EXCEPT_DIRECTORIES):
                    continue
                for basename in basenames:
                    path = Path(folder) / root / basename
                    if not basename.endswith(tuple(self.supported_formats)):
                        self.other_files.append(path)
                    else:
                        self.files.append(path)

        def worker(path: Path) -> File | None:
            try:
                return File(path=path)
            except OSError as e:
                logger.error(e)
            return None

        self.musics = self.parallel(
            worker,
            self.files,
            prefix='Loading musics',
            threads=threads,
        )

    def __repr__(self) -> str:
        return ' '.join(str(folder) for folder in self.folders)

    def empty_dirs(self, recursive: bool = True) -> Iterator[str]:
        for root_dir in self.folders:
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
