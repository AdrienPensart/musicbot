import pathlib
import logging
from os import scandir, walk, path, DirEntry
from typing import Iterator, Iterable, Tuple
import humanfriendly  # type: ignore

logger = logging.getLogger(__name__)

output_types = ["list", "json"]
except_directories = ['.Spotlight-V100', '.zfs', 'Android', 'LOST.DIR']
default_output_type = 'json'


def ensure(path: str) -> str:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)


def bytes_to_human(b: int) -> str:
    return str(humanfriendly.format_size(b))


def empty_dirs(root_dir: str, recursive: bool = True) -> Iterator[str]:
    dirs_list = []
    for root, dirs, files in walk(root_dir, topdown=False):
        if recursive:
            all_subs_empty = True
            for sub in dirs:
                full_sub = path.join(root, sub)
                if full_sub not in dirs_list:
                    all_subs_empty = False
                    break
        else:
            all_subs_empty = (not dirs)
        if all_subs_empty and not files:
            dirs_list.append(root)
            yield root


def find_files(directories: Iterable[str], supported_formats: Iterable[str]) -> Iterator[Tuple[str, str]]:
    directories = [path.abspath(d) for d in directories]
    for directory in directories:
        for root, _, files in walk(directory):
            if any(e in root for e in except_directories):
                continue
            for basename in files:
                filename = path.join(root, basename)
                if filename.endswith(tuple(supported_formats)):
                    yield (directory, filename)


def scantree(path: str, supported_formats: Iterable[str]) -> Iterator[DirEntry]:
    try:
        if '/.' in path:
            return
        with scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    if entry.name.endswith(tuple(supported_formats)):
                        yield entry
                elif entry.is_dir(follow_symlinks=False):
                    yield from scantree(entry.path, supported_formats)
    except PermissionError as e:
        logger.error(e)


def filecount(path: str, supported_formats: Iterable[str]) -> int:
    return len(list(scantree(path, supported_formats)))


def all_files(directory: str) -> Iterable[str]:
    for root, _, files in walk(directory):
        if any(e in root for e in except_directories):
            logger.debug(f"Invalid path {root}")
            continue
        for basename in files:
            yield path.join(root, basename)


default_checks = [
    'keywords',
    'strict_title',
    'title',
    'path',
    'genre',
    'album',
    'artist',
    'rating',
    'number'
]
