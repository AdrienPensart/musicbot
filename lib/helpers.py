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
from .mfilter import Filter, supported_formats

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

DEFAULT_MB_CONCURRENCY = 2
concurrency = [
    click.option('--concurrency', envvar='MB_CONCURRENCY', help='Number of coroutines', default=DEFAULT_MB_CONCURRENCY, show_default=True),
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


async def fullscan(db, folders=None, concurrency=1, crawl=False, sync=False):
    if folders is None:
        folders = await db.folders()
        folders = [f['name'] for f in folders]

    with click_spinner.spinner():
        files = [f for f in find_files(list(folders)) if f[1].endswith(tuple(supported_formats))]
    size = len(files) * 2 if crawl else len(files)
    with tqdm(total=size, file=sys.stdout, desc="Loading music", leave=True, position=0, disable=config.quiet) as bar:
#        if sync:    
#            sql = '''
#    delete from music_tags mt where mt.music_id = (select old.id from musics old where old.path = %(path)s limit 1);
#    with upsert_folder as (
#        insert into folders as f (name, created_at)
#        values (%(folder)s, now())
#        on conflict (name) do update set
#            updated_at=coalesce(EXCLUDED.updated_at, now()),
#            name=EXCLUDED.name
#        returning f.id as folder_id
#    ),
#    upsert_artist as (
#        insert into artists as a (name, created_at)
#        values (%(artist)s, now())
#        on conflict (name) do update set
#            updated_at=coalesce(EXCLUDED.updated_at, now()),
#            name=EXCLUDED.name
#        returning a.id as artist_iD
#    ),
#    upsert_album as (
#        insert into albums as al (artist_id, name, created_at)
#        values ((select artist_id from upsert_artist limit 1), %(album)s, now())
#        on conflict (artist_id, name) do update set
#            updated_at=coalesce(EXCLUDED.updated_at, now()),
#            name=EXCLUDED.name
#        returning al.id as album_id
#    ),
#    upsert_genre as (
#        insert into genres as g (name)
#        values (%(genre)s)
#        on conflict (name) do update set
#            updated_at=coalesce(EXCLUDED.updated_at, now()),
#            name=EXCLUDED.name
#        returning g.id as genre_id
#    ),
#    upsert_keywords as (
#        insert into tags as t (name)
#        select distinct k from unnest(%(keywords)s::text[]) k
#        on conflict (name) do update set
#            updated_at=coalesce(EXCLUDED.updated_at, now()),
#            name=EXCLUDED.name
#        returning t.id as tag_id
#    ),
#    upsert_music as (
#        insert into musics as m (artist_id, genre_id, folder_id, album_id, rating, duration, path, title, number, size, youtube, created_at)
#        values (
#            (select artist_id from upsert_artist limit 1),
#            (select genre_id from upsert_genre limit 1),
#            (select folder_id from upsert_folder limit 1),
#            (select album_id from upsert_album limit 1),
#            %(rating)s, %(duration)s, %(path)s, %(title)s, %(number)s, %(size)s, %(youtube)s, now())
#        on conflict (path) do update set
#            updated_at=coalesce(EXCLUDED.updated_at, now()),
#            artist_id=EXCLUDED.artist_id,
#            genre_id=EXCLUDED.genre_id,
#            folder_id=EXCLUDED.folder_id,
#            album_id=EXCLUDED.album_id,
#            rating=EXCLUDED.rating,
#            duration=EXCLUDED.duration,
#            title=EXCLUDED.title,
#            number=EXCLUDED.number,
#            size=EXCLUDED.size,
#            youtube=coalesce(EXCLUDED.youtube, m.youtube)
#        returning m.id as music_id
#    )
#    insert into music_tags (music_id, tag_id)
#    select m.music_id, k.tag_id from upsert_music m, upsert_keywords k
#    on conflict (music_id, tag_id) do nothing;
#    delete from tags t where t.id in (select t.id from tags t left join music_tags mt on t.id = mt.tag_id group by t.id having count(mt.music_id) = 0);
#'''
#            import psycopg2
#            with psycopg2.connect(db.connection_string) as conn:
#                with conn.cursor() as cur:
#                    for f in files:
#                        m = File(f[1], f[0])
#                        cur.execute(sql, m.to_dict())
#                        bar.update(1)
#                conn.commit()
#        else:
        async with (await db.pool).acquire() as connection:
            async with connection.transaction():
                for f in files:
                    m = File(f[1], f[0])
                    try:
                        await db.upsert(m)
                    except asyncpg.exceptions.CheckViolationError as e:
                        warning("Violation: {}".format(e))
                    bar.update(1)
    #with tqdm(total=size, file=sys.stdout, desc="Loading music", leave=True, position=0, disable=config.quiet) as bar:
    #    async def insert(semaphore, f):
    #        async with semaphore:
    #            try:
    #                m = File(f[1], f[0])
    #                if crawl:
    #                    await m.find_youtube()
    #                    bar.update(1)
    #                debug(m.to_list())
    #                await db.upsert(m)
    #                bar.update(1)
    #            except asyncpg.exceptions.CheckViolationError as e:
    #                warning("Violation: {}".format(e))
    #    semaphore = asyncio.BoundedSemaphore(concurrency)
    #    tasks = [asyncio.ensure_future(insert(semaphore, f)) for f in files]
    #    await asyncio.gather(*tasks)
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
                    debug('Creatin/modifying DB for: {}'.format(path))
                    f = File(path, folder['name'])
                    debug(f.to_list())
                    await db.upsert(f)
                    # await db.refresh()
                    return

        async def on_modified(self, event):
            await self.update(event.src_path)

        async def on_created(self, event):
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
