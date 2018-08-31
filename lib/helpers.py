# -*- coding: utf-8 -*-
import asyncio
import time
import uvloop
import click
import asyncpg
import click_spinner
import logging
from tqdm import tqdm
from functools import wraps
from hachiko.hachiko import AIOEventHandler
from . import youtube
from .config import config
from .file import File
from .lib import secondsToHuman, find_files
from .mfilter import Filter, supported_formats

logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

DEFAULT_MB_CONCURRENCY = 8
concurrency = [
    click.option('--concurrency', envvar='MB_CONCURRENCY', help='Number of coroutines', default=DEFAULT_MB_CONCURRENCY, show_default=True),
]


def timeit(f):
    async def process(f, *args, **params):
        if asyncio.iscoroutinefunction(f):
            return await f(*args, **params)
        return f(*args, **params)

    @wraps(f)
    async def helper(*args, **params):
        start = time.time()
        result = await process(f, *args, **params)
        for_human = secondsToHuman(time.time() - start)
        if config.timings:
            logger.info('%s: %s', f.__name__, for_human)
        return result

    return helper


async def refresh_db(db):
    await db.refresh()


@timeit
async def crawl_musics(db, mf=None, concurrency=1):
    if mf is None:
        mf = Filter(youtube='')
    musics = await db.musics(mf)
    with tqdm(desc='Youtube musics', total=len(musics), disable=config.quiet) as pbar:
        async def search(semaphore, m):
            async with semaphore:
                result = await youtube.search(m['artist'], m['title'], m['duration'])
                pbar.update(1)
                await db.set_music_youtube(m['path'], result)
        semaphore = asyncio.BoundedSemaphore(concurrency)
        requests = [asyncio.ensure_future(search(semaphore, m)) for m in musics]
        await asyncio.gather(*requests)
    await db.refresh()


@timeit
async def crawl_albums(db, mf=None, youtube_album='', concurrency=1):
    if mf is None:
        mf = Filter()
    albums = await db.albums(mf, youtube_album)
    with tqdm(desc='Youtube albums', total=len(albums), disable=config.quiet) as pbar:
        async def search(semaphore, a):
            async with semaphore:
                result = await youtube.search(a['artist'], a['name'] + ' full album', a['duration'])
                await db.set_album_youtube(a['name'], result)
                pbar.update(1)
        semaphore = asyncio.BoundedSemaphore(concurrency)
        requests = [asyncio.ensure_future(search(semaphore, a)) for a in albums]
        await asyncio.gather(*requests)
    await db.refresh()


@timeit
async def fullscan(db, folders=None, crawl=False):
    if folders is None:
        folders = await db.folders()
        folders = [f['name'] for f in folders]

    with click_spinner.spinner(disable=config.quiet):
        files = [f for f in find_files(list(folders)) if f[1].endswith(tuple(supported_formats))]
    size = len(files) if crawl else len(files)
    with tqdm(total=size, desc="Loading music", disable=config.quiet) as pbar:
        async with (await db.pool).acquire() as connection:
            async with connection.transaction():
                for f in files:
                    m = File(f[1], f[0])
                    try:
                        await db.upsert(m)
                    except asyncpg.exceptions.CheckViolationError as e:
                        logger.warning("Violation: %s", e)
                    pbar.update(1)
    await db.refresh()


async def watcher(db):
    logger.info('Starting to watch folders')
    folders = await db.folders()

    class MusicWatcherHandler(AIOEventHandler):
        async def update(self, path):
            for folder in folders:
                if path.startswith(folder['name']) and path.endswith(tuple(supported_formats)):
                    logger.debug('Creatin/modifying DB for: %s', path)
                    f = File(path, folder['name'])
                    logger.debug(f.to_list())
                    await db.upsert(f)
                    # await db.refresh()
                    return

        async def on_modified(self, event):
            await self.update(event.src_path)

        async def on_created(self, event):
            await self.update(event.src_path)

        async def on_deleted(self, event):
            logger.debug('Deleting entry in DB for: %s %s', event.src_path, event.event_type)
            await db.delete(event.src_path)
            await db.refresh()

        async def on_moved(self, event):
            logger.debug('Moving entry in DB for: %s %s', event.src_path, event.event_type)
            await db.delete(event.src_path)
            await self.update(event.dest_path)

    evh = MusicWatcherHandler()
    from watchdog.observers import Observer
    observer = Observer()
    for f in folders:
        logger.info('Watching: %s', f['name'])
        observer.schedule(evh, f['name'], recursive=True)
    observer.start()
    try:
        while True:
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


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
        if config.dry:
            args = [str(a) for a in args] + ["%s=%s" % (k, v) for (k, v) in kwargs.items()]
            logger.info('DRY RUN: %s(%s)', f.__name__, ','.join(args))
            await asyncio.sleep(0)
        else:
            return await f(*args, **kwargs)
    return wrapper
