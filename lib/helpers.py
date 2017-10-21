# -*- coding: utf-8 -*-
import click
import asyncio
import asyncpg
from functools import update_wrapper
from logging import debug
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, basicConfig, getLogger

verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}

global_options = [
    click.option('--verbosity', help='Verbosity levels', default='error', type=click.Choice(verbosities.keys())),
    click.option('--dry-run', help='Take no real action', default=False, is_flag=True),
    click.option('--quiet', help='Silence any output (like progress bars)', default=False, is_flag=True)
]

db_options = [
    click.option('--host', help='DB host', default='localhost'),
    click.option('--port', help='DB port', default=5432),
    click.option('--db', help='DB name', default='musicbot'),
    click.option('--user', help='DB user', default='postgres'),
    click.option('--password', help='DB password', default='musicbot')
]

default_formats = ["mp3", "flac"]
filter_options = [
    click.option('--filter', help='Filter file to load'),
    click.option('--limit', help='Fetch a maximum limit of music'),
    click.option('--youtube', help='Select musics with a youtube link', default=None, is_flag=True),
    click.option('--formats', help='Select musics with file format, comma separated', default=','.join(default_formats)),
    click.option('--no-formats', help='Filter musics without format, comma separated, can be "None" for empty string'),
    click.option('--keywords', help='Select musics with keywords, comma separated, can be "None" for empty string'),
    click.option('--no-keywords', help='Filter musics without keywords, comma separated, can be "None" for empty string'),
    click.option('--artists', help='Select musics with artists, comma separated, can be "None" for empty string'),
    click.option('--no-artists', help='Filter musics without artists, comma separated, can be "None" for empty string'),
    click.option('--albums', help='Select musics with albums, comma separated, can be "None" for empty string'),
    click.option('--no-albums', help='Filter musics without albums, comma separated, can be "None" for empty string'),
    click.option('--titles', help='Select musics with titles, comma separated, can be "None" for empty string'),
    click.option('--no-titles', help='Filter musics without titless, comma separated, can be "None" for empty string'),
    click.option('--genres', help='Select musics with genres, comma separated, can be "None" for empty string'),
    click.option('--no-genres', help='Filter musics without genres, comma separated, can be "None" for empty string'),
    click.option('--min-duration', help='Minimum duration filter (hours:minutes:seconds)'),
    click.option('--max-duration', help='Maximum duration filter (hours:minutes:seconds))'),
    click.option('--min-size', help='Minimum file size filter (in bytes)'),
    click.option('--max-size', help='Maximum file size filter (in bytes)'),
    click.option('--min-rating', help='Minimum rating (between {default_min_rating} and {default_max_rating})'),
    click.option('--max-rating', help='Maximum rating (between {default_min_rating} and {default_max_rating})')
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def coro(f):
    f = asyncio.coroutine(f)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        return loop.run_until_complete(f(*args, **kwargs))
    return update_wrapper(wrapper, f)


class GlobalContext(object):
    def __init__(self):
        self.quiet = False
        self.dry_run = False
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


class DbContext(object):
    settings = {
        'host': 'localhost',
        'port': 5432,
        'database': 'musicbot',
        'user': 'postgres',
        'password': 'musicbot', }

    def __init__(self, **kwargs):
        self.settings.update(kwargs)
        self._pool = None

    def connection_string(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(self.settings['host'], self.settings['password'], self.settings['host'], self.settings['port'], self.settings['database'])

    @property
    async def pool(self):
        if self._pool is None:
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(**self.settings)
        return self._pool

    async def fetch(self, *args, **kwargs):
        return (await (await self.pool).fetch(*args, **kwargs))


global_context = click.make_pass_decorator(GlobalContext, ensure=True)
db_context = click.make_pass_decorator(DbContext, ensure=True)
