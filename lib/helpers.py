# -*- coding: utf-8 -*-
import asyncio
import time
import uvloop
import click
import sys
import asyncpg
import click_spinner
from tqdm import tqdm
from functools import wraps
from logging import warning, debug, info
from hachiko.hachiko import AIOEventHandler
from . import youtube
from .config import config
from .file import File
from .lib import secondsToHuman, find_files
from .filter import Filter, supported_formats

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

concurrency = [
    click.option('--concurrency', envvar='MB_CONCURRENCY', help='Number of coroutines', default=32),
]


async def refresh_db(db):
    await db.refresh()


async def crawl_musics(db, mf=None, concurrency=1):
    if mf is None:
        mf = Filter(youtube='')
    musics = await db.musics(mf)
    with tqdm(desc='Youtube musics', total=len(musics), disable=config.quiet) as bar:
        async def search(semaphore, m):
            async with semaphore:
                result = await youtube.search(m['artist'], m['title'], m['duration'])
                await db.set_music_youtube(m['path'], result)
                bar.update(1)
        semaphore = asyncio.BoundedSemaphore(concurrency)
        requests = [asyncio.ensure_future(search(semaphore, m)) for m in musics]
        await asyncio.gather(*requests)
    await db.refresh()


async def crawl_albums(db, mf=None, youtube_album='', concurrency=1):
    if mf is None:
        mf = Filter()
    albums = await db.albums(mf, youtube_album)
    with tqdm(desc='Youtube albums', total=len(albums), disable=config.quiet) as bar:
        async def search(semaphore, a):
            async with semaphore:
                result = await youtube.search(a['artist'], a['name'] + ' full album', a['duration'])
                await db.set_album_youtube(a['name'], result)
                bar.update(1)
        semaphore = asyncio.BoundedSemaphore(concurrency)
        requests = [asyncio.ensure_future(search(semaphore, a)) for a in albums]
        await asyncio.gather(*requests)
    await db.refresh()


async def fullscan(db, folders=None, concurrency=1, crawl=False):
    if folders is None:
        folders = await db.folders()
        folders = [f['name'] for f in folders]

    with click_spinner.spinner():
        files = [f for f in find_files(list(folders)) if f[1].endswith(tuple(supported_formats))]
    size = len(files) * 2 if crawl else len(files)
    with tqdm(total=size, file=sys.stdout, desc="Loading music", leave=True, position=0, disable=config.quiet) as bar:
        async def insert(semaphore, f):
            async with semaphore:
                try:
                    m = File(f[1], f[0])
                    if crawl:
                        await m.find_youtube()
                        bar.update(1)
                    debug(m.to_list())
                    await db.upsert(m)
                    bar.update(1)
                except asyncpg.exceptions.CheckViolationError as e:
                    warning("Violation: {}".format(e))
        semaphore = asyncio.BoundedSemaphore(concurrency)
        tasks = [asyncio.ensure_future(insert(semaphore, f)) for f in files]
        await asyncio.gather(*tasks)
    await db.refresh()


async def watcher(db):
    info('Starting to watch folders')
    folders = await db.folders()

    class MusicWatcherHandler(AIOEventHandler):

        def __init__(self, loop=None):
            super().__init__(loop)

        async def update(self, path):
            for folder in folders:
                if path.startswith(folder['name']) and path.endswith(tuple(supported_formats)):
                    f = File(path, folder['name'])
                    debug(f.to_list())
                    await db.upsert(f)
                    # await db.refresh()
                    return

        async def on_modified(self, event):
            debug('Modifying DB for: {} {}'.format(event.src_path, event.event_type))
            await self.update(event.src_path)

        async def on_created(self, event):
            debug('Creating entry DB for: {} {}'.format(event.src_path, event.event_type))
            await self.update(event.src_path)

        async def on_deleted(self, event):
            debug('Deleting entry in DB for: {} {}'.format(event.src_path, event.event_type))
            await db.delete(event.src_path)
            await db.refresh()

        async def on_moved(self, event):
            debug('Moving entry in DB for: {} {}'.format(event.src_path, event.event_type))
            await db.delete(event.src_path)
            await self.update(event.dest_path)

    evh = MusicWatcherHandler()
    from watchdog.observers import Observer
    observer = Observer()
    for f in folders:
        info('Watching: {}'.format(f['name']))
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
        for_human = secondsToHuman(time.time() - start)
        debug('{}: {}'.format(f.__name__, for_human))
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
        if config.dry:
            args = [str(a) for a in args] + ["%s=%s" % (k, v) for (k, v) in kwargs.items()]
            info('DRY RUN: {}({})'.format(f.__name__, ','.join(args)))
            await asyncio.sleep(0)
        else:
            return await f(*args, **kwargs)
    return wrapper
