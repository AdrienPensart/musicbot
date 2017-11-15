# -*- coding: utf-8 -*-
import click
import asyncio
import time
import uvloop
from functools import wraps
from logging import debug, info
from . import filter
from .config import Config

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


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
    click.option('--formats', help='Select musics with file format', default=filter.default_formats, multiple=True),
    click.option('--no-formats', help='Filter musics without format', multiple=True),
    click.option('--keywords', help='Select musics with keywords', multiple=True),
    click.option('--no-keywords', help='Filter musics without keywords', multiple=True),
    click.option('--artists', help='Select musics with artists', multiple=True),
    click.option('--no-artists', help='Filter musics without artists', multiple=True),
    click.option('--albums', help='Select musics with albums', multiple=True),
    click.option('--no-albums', help='Filter musics without albums', multiple=True),
    click.option('--titles', help='Select musics with titles', multiple=True),
    click.option('--no-titles', help='Filter musics without titless', multiple=True),
    click.option('--genres', help='Select musics with genres', multiple=True),
    click.option('--no-genres', help='Filter musics without genres', multiple=True),
    click.option('--min-duration', help='Minimum duration filter (hours:minutes:seconds)'),
    click.option('--max-duration', help='Maximum duration filter (hours:minutes:seconds))'),
    click.option('--min-size', help='Minimum file size filter (in bytes)'),
    click.option('--max-size', help='Maximum file size filter (in bytes)'),
    click.option('--min-rating', help='Minimum rating', type=click.Choice(filter.rating_choices)),
    click.option('--max-rating', help='Maximum rating', type=click.Choice(filter.rating_choices)),
    click.option('--relative', help='Generate relatives paths', is_flag=True),
    click.option('--shuffle', help='Randomize selection', is_flag=True),
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
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapper


def drier(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        if Config.dry:
            args = [str(a) for a in args] + ["%s=%s" % (k, v) for (k, v) in kwargs.items()]
            info('DRY RUN: {}({})'.format(f.__name__, ','.join(args)))
            await asyncio.sleep(0)
        else:
            return await f(*args, **kwargs)
    return wrapper
