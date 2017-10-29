# -*- coding: utf-8 -*-
import click
import sys
import asyncio
from tqdm import tqdm
from logging import debug, info
from lib import helpers, lib, file, database, filter


@click.group(invoke_without_command=False)
@helpers.add_options(helpers.db_options)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@helpers.add_options(helpers.filter_options)
@click.argument('folders', nargs=-1)
@click.pass_context
def find(ctx, folders, **kwargs):
    files = lib.find_files(folders)
    for f in files:
        print(f[1])


@cli.command()
@helpers.coro
@click.argument('folders', nargs=-1)
@click.pass_context
async def scan(ctx, folders, **kwargs):
    lib.raise_limits()
    files = list(lib.find_files(list(folders)))
    # musics = []
    with tqdm(total=len(files), file=sys.stdout, desc="Music loading", leave=True, position=0, disable=ctx.obj.config.quiet) as bar:
        for f in files:
            if f[1].endswith(tuple(filter.default_formats)):
                m = file.File(f[1], f[0])
                await ctx.obj.db.upsert(m)
                # musics.append(m)
                # musics.append((m.artist, m.album, m.genre, m.folder, m.youtube, m.number, m.rating, m.duration, m.size, m.title, m.path, m.keywords), )
                # await ctx.obj.db.append(m)
            bar.update(1)
    # await ctx.obj.db.appendmany(musics)
    # await ctx.obj.db.upsertall(musics)


@cli.command()
@helpers.coro
@click.pass_context
async def rescan(ctx, **kwargs):
    folders = await ctx.obj.db.folders()
    for folder in folders:
        info('rescanning {}'.format(folder))


@cli.command()
@helpers.coro
@click.pass_context
async def watch(ctx, **kwargs):
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler

    class MusicWatcherHandler(PatternMatchingEventHandler):
        patterns = []

        def __init__(self, loop=None):
            super().__init__()
            self.loop = loop or asyncio.get_event_loop()
            self.patterns = ['*.' + f for f in filter.default_formats]

        def update(self, path):
            for folder in folders:
                if path.startswith(folder['name']):
                    f = file.File(path, folder['name'])
                    c = ctx.obj.db.upsert(f)
                    asyncio.run_coroutine_threadsafe(c, self.loop)
                    # ctx.obj.db.upsert(f)
                    break

        def on_modified(self, event):
            debug('Modifying DB for: {} {}'.format(event.src_path, event.event_type))
            self.update(event.src_path)

        def on_created(self, event):
            debug('Creating entry DB for: {} {}'.format(event.src_path, event.event_type))
            self.update(event.src_path)

        def on_deleted(self, event):
            debug('Deleting entry in DB for: {} {}'.format(event.src_path, event.event_type))
            c = ctx.obj.db.delete(event.src_path)
            asyncio.run_coroutine_threadsafe(c, self.loop)

        def on_moved(self, event):
            debug('Moving entry in DB for: {} {}'.format(event.src_path, event.event_type))
            c = ctx.obj.db.delete(event.src_path)
            asyncio.run_coroutine_threadsafe(c, self.loop)
            self.update(event.dest_path)

    lib.raise_limits()
    loop = asyncio.get_event_loop()
    event_handler = MusicWatcherHandler(loop)
    observer = Observer()
    folders = await ctx.obj.db.folders()
    for f in folders:
        info('Watching: {}'.format(f['name']))
        observer.schedule(event_handler, f['name'], recursive=True)
    observer.start()
    try:
        while True:
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
