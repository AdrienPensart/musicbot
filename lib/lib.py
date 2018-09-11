import os
import re
import sys
import logging
import humanfriendly
from timeit import default_timer as timer

logger = logging.getLogger(__name__)

output_types = ["list", "json"]
default_output_type = 'json'


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


def bytes_to_human(b):
    return humanfriendly.format_size(b)


def seconds_to_human(s):
    import datetime
    return str(datetime.timedelta(seconds=s))


def empty_dirs(root_dir, recursive=True):
    empty_dirs = []
    for root, dirs, files in os.walk(root_dir, topdown=False):
        if recursive:
            all_subs_empty = True
            for sub in dirs:
                full_sub = os.path.join(root, sub)
                if full_sub not in empty_dirs:
                    all_subs_empty = False
                    break
        else:
            all_subs_empty = (not dirs)
        if all_subs_empty and is_empty(files):
            empty_dirs.append(root)
            yield root


def is_empty(files):
    return len(files) == 0


class Benchmark:
    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        self.start = timer()
        return self

    def __exit__(self, *args):
        t = timer() - self.start
        logger.info("%s : %0.3g seconds", self.msg, t)
        self.time = t


class LazyProperty:
    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


def raise_limits():
    import resource
    try:
        _, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        logger.info("Current limits, soft and hard : %s %s", _, hard)
        resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
        return True
    except Exception as e:
        logger.critical('You may need to check ulimit parameter: %s', e)
        return False


def restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)


def find_files(directories):
    directories = [os.path.abspath(d) for d in directories]
    for directory in directories:
        for root, _, files in os.walk(directory):
            if '.zfs' in root:
                continue
            for basename in files:
                filename = os.path.join(root, basename)
                yield (directory, filename)


def scantree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def filecount(path):
    return len(list(scantree(path)))


def all_files(directory):
    for root, _, files in os.walk(directory):
        for basename in files:
            yield os.path.join(root, basename)


def first(iterable, default=None):
    if iterable:
        if isinstance(iterable, str):
            return iterable
        for item in iterable:
            return item
    return default


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def duration_to_seconds(duration):
    if re.match(r'\d+s', duration):
        return int(duration[:-1])
    if re.match(r'\d+m', duration):
        return int(duration[:-1]) * 60
    if re.match(r'\d+h', duration):
        return int(duration[:-1]) * 3600
    raise ValueError(duration)


def seconds_to_str(duration):
    import datetime
    return str(datetime.timedelta(seconds=duration))


default_checks = ['keywords', 'strict_title', 'title', 'path',
                  'genre', 'album', 'artist', 'rating', 'number']
