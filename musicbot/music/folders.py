from typing import List, Iterator, Iterable, Optional
from pathlib import Path
import os
import logging
from musicbot.object import MusicbotObject
from musicbot.defaults import DEFAULT_EXTENSIONS
from musicbot.music.file import File

logger = logging.getLogger(__name__)

except_directories = ['.Spotlight-V100', '.zfs', 'Android', 'LOST.DIR']


class Folders:
    def __init__(self, folders: Iterable[Path], extensions: Optional[Iterable[str]]):
        self.supported_formats = extensions if extensions is not None else DEFAULT_EXTENSIONS
        self.folders = [folder.resolve() for folder in folders]
        self.files = []
        self.other_files: List[Path] = []

        for folder in self.folders:
            for root, _, basenames in os.walk(folder):
                if any(e in root for e in except_directories):
                    continue
                for basename in basenames:
                    path = Path(folder) / root / basename
                    if not basename.endswith(tuple(self.supported_formats)):
                        self.other_files.append(path)
                    else:
                        self.files.append(path)

        def worker(path: Path) -> Optional[File]:
            try:
                return File(path=path)
            except KeyboardInterrupt as e:
                logger.error(f'interrupted : {e}')
                raise
            except OSError as e:
                logger.error(e)
            return None
        self.musics = MusicbotObject.parallel(worker, self.files)

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
