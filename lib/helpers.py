# -*- coding: utf-8 -*-
import click
import asyncio
import time
from functools import wraps
from logging import debug, info
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, basicConfig, getLogger
from . import filter, playlist

verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}

global_options = [
    click.option('--verbosity', help='Verbosity levels', default='error', type=click.Choice(verbosities.keys())),
    click.option('--dry', help='Take no real action', default=False, is_flag=True),
    click.option('--quiet', help='Silence any output (like progress bars)', default=False, is_flag=True)
]

db_options = [
    click.option('--host', help='DB host', default='localhost'),
    click.option('--port', help='DB port', default=5432),
    click.option('--database', help='DB name', default='musicbot'),
    click.option('--user', help='DB user', default='postgres'),
    click.option('--password', help='DB password', default='musicbot')
]

default_fields = ['title', 'album', 'artist', 'genre', 'path', 'keywords', 'folder', 'rating', 'number', 'folder', 'youtube', 'duration', 'size']
tag_options = [
    click.option('--fields', help='Show only those fields', default=default_fields, multiple=True),
    click.option('--output', help='Tags output format'),
]

filter_options = [
    click.option('--filter', help='Filter file to load'),
    click.option('--limit', help='Fetch a maximum limit of music'),
    click.option('--youtube', help='Select musics with a youtube link', default=None, is_flag=True),
    click.option('--formats', help='Select musics with file format, comma separated', default=filter.default_formats, multiple=True),
    click.option('--no-formats', help='Filter musics without format, comma separated, can be "None" for empty string', multiple=True),
    click.option('--keywords', help='Select musics with keywords, comma separated, can be "None" for empty string', multiple=True),
    click.option('--no-keywords', help='Filter musics without keywords, comma separated, can be "None" for empty string', multiple=True),
    click.option('--artists', help='Select musics with artists, comma separated, can be "None" for empty string', multiple=True),
    click.option('--no-artists', help='Filter musics without artists, comma separated, can be "None" for empty string', multiple=True),
    click.option('--albums', help='Select musics with albums, comma separated, can be "None" for empty string', multiple=True),
    click.option('--no-albums', help='Filter musics without albums, comma separated, can be "None" for empty string', multiple=True),
    click.option('--titles', help='Select musics with titles, comma separated, can be "None" for empty string', multiple=True),
    click.option('--no-titles', help='Filter musics without titless, comma separated, can be "None" for empty string', multiple=True),
    click.option('--genres', help='Select musics with genres, comma separated, can be "None" for empty string', multiple=True),
    click.option('--no-genres', help='Filter musics without genres, comma separated, can be "None" for empty string', multiple=True),
    click.option('--min-duration', help='Minimum duration filter (hours:minutes:seconds)'),
    click.option('--max-duration', help='Maximum duration filter (hours:minutes:seconds))'),
    click.option('--min-size', help='Minimum file size filter (in bytes)'),
    click.option('--max-size', help='Maximum file size filter (in bytes)'),
    click.option('--min-rating', help='Minimum rating (between {default_min_rating} and {default_max_rating})'),
    click.option('--max-rating', help='Maximum rating (between {default_min_rating} and {default_max_rating})')
]

playlist_options = [
    click.option('--relative', help='Generate relatives paths', is_flag=True),
    click.option('--shuffle', help='Randomize selection', is_flag=True),
    click.option('--path', help='Playlist output file path'),
    click.option('--type', help='Playlist format', type=click.Choice(playlist.playlist_types), default=playlist.default_playlist_type)
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def timeit(f):
    async def process(f, *args, **params):
        if asyncio.iscoroutinefunction(f):
            return await f(*args, **params)
        else:
            return f(*args, **params)

    @wraps(f)
    async def helper(*args, **params):
        start = time.time()
        result = await process(f, *args, **params)
        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)
        debug('{}: {}'.format(f.__name__, time.time() - start))
        return result

    return helper


def coro(f):
    f = asyncio.coroutine(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if config.verbosity is DEBUG:
            loop.set_debug(True)
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapper


def drier(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        if config.dry:
            args = [str(a) for a in args] + ["%s=%s" % (k, v) for (k, v) in kwargs.items()]
            info('DRY RUN: {}({})'.format(f.__name__, ','.join(args)))
            await asyncio.sleep(0)
        else:
            return await f(*args, **kwargs)
    return wrapper


class GlobalContext(object):
    def __init__(self):
        self.quiet = False
        self.dry = False
        self._verbosity = ERROR

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        self._verbosity = verbosity
        level = verbosities[verbosity]
        basicConfig(level=level)
        getLogger('asyncio').setLevel(level)
        debug('new verbosity: {}'.format(self.verbosity))

    def __repr__(self):
        return '{} {} {}'.format(self.quiet, self.dry, self._verbosity)


config = GlobalContext()
