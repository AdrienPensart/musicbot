# -*- coding: utf-8 -*-
import click
import asyncio
import asyncpg
import sys
import os
import time
from functools import wraps
from logging import debug, info
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, basicConfig, getLogger

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
        info('{}: {}'.format(f.__name__, time.time() - start))
        return result

    return helper


def coro(f):
    f = asyncio.coroutine(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
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


class DbContext(object):
    settings = {
        'host': 'localhost',
        'port': 5432,
        'database': 'musicbot',
        'user': 'postgres',
        'password': 'musicbot', }
    schema = 'public'

    def __init__(self, **kwargs):
        self.settings.update(kwargs)
        self._pool = None

    def connection_string(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(self.settings['host'], self.settings['password'], self.settings['host'], self.settings['port'], self.settings['database'])

    # def __repr__(self):
    #     return self.connection_string()

    def __str__(self):
        return self.connection_string()

    @property
    async def pool(self):
        if self._pool is None:
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(**self.settings)
        return self._pool

    @timeit
    async def fetch(self, *args, **kwargs):
        info('fetching: {}'.format(*args))
        return (await (await self.pool).fetch(*args, **kwargs))

    @drier
    @timeit
    async def executefile(self, filepath):
        schema_path = os.path.join(os.path.dirname(sys.argv[0]), filepath)
        info('loading schema: {}'.format(schema_path))
        with open(schema_path, "r") as s:
            sql = s.read()
            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    await connection.execute(sql)

    @drier
    @timeit
    async def execute(self, sql):
        info(sql)
        async with (await self.pool).acquire() as connection:
            async with connection.transaction():
                await connection.execute(sql)

    async def create(self):
        debug('db create')
        sql = 'create schema if not exists {}'.format(self.schema)
        await self.execute(sql)
        await self.executefile('lib/musicbot.sql')

    async def drop(self):
        debug('db drop')
        sql = 'drop schema if exists {} cascade'.format(self.schema)
        await self.execute(sql)

    async def clear(self):
        debug('clear')
        await self.drop()
        await self.create()

    async def folders(self):
        sql = '''select name from folders'''
        return await self.fetch(sql)


config = GlobalContext()
