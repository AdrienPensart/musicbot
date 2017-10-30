import os
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk
import re
import yaml
from . import file
from timeit import default_timer as timer
from logging import info, error, critical


quiet = False
output_types = ["list", "json"]
default_output_type = 'json'


def convert_rating(arg):
    if type(arg) is float:
        return arg / 5.0
    return float(first(arg)) / 5.0


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
            all_subs_empty = (len(dirs) == 0)
        if all_subs_empty and is_empty(files):
            empty_dirs.append(root)
            yield root


def is_empty(files):
    return len(files) == 0


class benchmark(object):

    def __init__(self, msg, fmt="%0.3g"):
        self.msg = msg
        self.fmt = fmt

    def __enter__(self):
        self.start = timer()
        return self

    def __exit__(self, *args):
        t = timer() - self.start
        info(("%s : " + self.fmt + " seconds") % (self.msg, t))
        self.time = t


class lazy_property(object):

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


def dump_filter(data, path):
    with open(path, 'w') as stream:
        yaml.dump(data, stream, default_flow_style=False)


def load_filter(path):
    with open(path, 'r') as stream:
        mf = filter.Filter()
        mf = yaml.load(stream)
        return mf


def raise_limits():
    import resource
    try:
        _, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        info("Current limits, soft and hard : {} {}".format(_, hard))
        resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
    except ValueError:
        error("Exceeds limit {}, infinity is {}".format(hard, resource.RLIM_INFINITY))
    except resource.error:
        return False
    except OSError as e:
        critical('You may need to check ulimit parameter: {}'.format(e))
        raise e
    return True


def find_files(directories):
    directories = [os.path.abspath(d) for d in directories]
    for directory in directories:
        for root, _, files in walk(directory):
            for basename in files:
                filename = os.path.join(root, basename)
                yield (directory, filename)


def scantree(path):
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def filecount(path):
    return len(list(scantree(path)))


def all_files(directory):
    for root, _, files in walk(directory):
        for basename in files:
            yield os.path.join(root, basename)


def first(iterable, default=None):
    if iterable:
        if type(iterable) is str:
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
    if re.match("\d+s", duration):
        return int(duration[:-1])
    if re.match("\d+m", duration):
        return int(duration[:-1]) * 60
    if re.match("\d+h", duration):
        return int(duration[:-1]) * 3600
    raise ValueError(duration)


def seconds_to_str(duration):
    import datetime
    return str(datetime.timedelta(seconds=duration))


default_checks = ['keywords', 'strict_title', 'title', 'path',
                  'genre', 'album', 'artist', 'rating', 'number']


def check_consistency(musics, checks, no_checks):
    report = []
    for m in musics:
        try:
            if 'keywords' in checks and 'keywords' not in no_checks:
                f = file.MusicFile(m.path)
                if m.path.endswith('.flac'):
                    if f.comment and not f.description:
                        report.append('Comment (' + f.comment +
                                      ') used in flac: ' + m.path)
                if m.path.endswith('.mp3'):
                    if f.description and not f.comment:
                        report.append(
                            'Description (' +
                            f.description +
                            ') used in mp3 : ' +
                            m.path)
            if 'title' in checks and 'title' not in no_checks and not len(m.title):
                report.append("No title  : '" + m.title + "' on " + m.path)
            if 'strict_title' in checks and 'strict_title' not in no_checks:
                filename = os.path.basename(m.path)
                if filename == "{} - {}.mp3".format(str(m.number).zfill(2), m.title):
                    continue
                if filename == "{} - {}.flac".format(str(m.number).zfill(2), m.title):
                    continue
                report.append("Invalid title format, '{}' should start by '{}'".
                              format(filename, '{} - {}'.format(str(m.number).zfill(2), m.title)))
            if 'path' in checks and 'path' not in no_checks and m.artist not in m.path:
                report.append("Artist invalid : " +
                              m.artist + " is not in " + m.path)
            if 'genre' in checks and 'genre' not in no_checks and m.genre == '':
                report.append("No genre : " + m.path)
            if 'album' in checks and 'album' not in no_checks and m.album == '':
                report.append("No album :i " + m.path)
            if 'artist' in checks and 'artist' not in no_checks and m.artist == '':
                report.append("No artist : " + m.path)
            if 'rating' in checks and 'rating' not in no_checks and m.rating == 0.0:
                report.append("No rating : " + m.path)
            if 'number' in checks and m.number == -1:
                report.append("Invalid track number : " + m.path)
        except OSError:
            report.append("Could not open file : " + m.path)
    return report
