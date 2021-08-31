from typing import List, Iterator, Iterable, Collection
from pathlib import Path
import os
import logging
import attr
from musicbot.timing import timeit
from musicbot.object import MusicbotObject
from musicbot.music.file import File, supported_formats

logger = logging.getLogger(__name__)

except_directories = ['.Spotlight-V100', '.zfs', 'Android', 'LOST.DIR']


@attr.s(auto_attribs=True, repr=False)
class Folders:
    folders: Iterable[Path]

    def __repr__(self):
        return ' '.join(str(folder) for folder in self.folders)

    @timeit
    def musics(self) -> Collection["File"]:
        files: List[Path] = self.supported_files(supported_formats)

        def worker(path: Path):
            try:
                return File(path=path)
            except KeyboardInterrupt as e:
                logger.error(f'interrupted : {e}')
                raise
            except OSError as e:
                logger.error(e)
            return None
        return MusicbotObject.parallel(worker, files)

    def empty_dirs(self, recursive: bool = True) -> Iterator[str]:
        for root_dir in self.folders:
            dirs_list = []
            for root, dirs, files in os.walk(root_dir.resolve(), topdown=False):
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

    def supported_files(self, supported_formats: Iterable[str]) -> List[Path]:
        files: List[Path] = []
        for folder in self.folders:
            for root, _, basenames in os.walk(folder.resolve()):
                if any(e in root for e in except_directories):
                    continue
                for basename in basenames:
                    if not basename.endswith(tuple(supported_formats)):
                        continue
                    files.append(Path(folder) / root / basename)
        return files
