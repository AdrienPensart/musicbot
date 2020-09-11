import os
import typing
import re
import logging
import humanfriendly

logger = logging.getLogger(__name__)

output_types = ["list", "json"]
except_directories = ['.Spotlight-V100', '.zfs', 'Android', 'LOST.DIR']
default_output_type = 'json'


def bytes_to_human(b) -> str:
    return humanfriendly.format_size(b)


def empty_dirs(root_dir, recursive=True) -> typing.Iterator[str]:
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


def find_files(directories, supported_formats) -> typing.Iterator[typing.Tuple[str, str]]:
    directories = [os.path.abspath(d) for d in directories]
    for directory in directories:
        for root, _, files in os.walk(directory):
            if any(e in root for e in except_directories):
                continue
            for basename in files:
                filename = os.path.join(root, basename)
                if filename.endswith(tuple(supported_formats)):
                    yield (directory, filename)


def scantree(path, supported_formats) -> typing.Iterator[os.DirEntry]:
    try:
        if '/.' in path:
            return
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from scantree(entry.path, supported_formats)
            else:
                if entry.name.endswith(tuple(supported_formats)):
                    yield entry
    except PermissionError as e:
        logger.error(e)


def filecount(path, supported_formats) -> int:
    return len(list(scantree(path, supported_formats)))


def all_files(directory) -> str:
    for root, _, files in os.walk(directory):
        if any(e in root for e in except_directories):
            logger.debug(f"Invalid path {root}")
            continue
        for basename in files:
            yield os.path.join(root, basename)


def first(iterable, default=None) -> typing.Any:
    if iterable:
        if isinstance(iterable, str):
            return iterable
        for item in iterable:
            return item
    return default


def num(s) -> typing.Union[int, float]:
    try:
        return int(s)
    except ValueError:
        return float(s)


def duration_to_seconds(duration) -> int:
    if re.match(r'\d+s', duration):
        return int(duration[:-1])
    if re.match(r'\d+m', duration):
        return int(duration[:-1]) * 60
    if re.match(r'\d+h', duration):
        return int(duration[:-1]) * 3600
    raise ValueError(f"bad duration {duration}")


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
