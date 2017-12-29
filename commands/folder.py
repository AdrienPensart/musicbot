# -*- coding: utf-8 -*-
import click
import sys
import os
import asyncio
import asyncpg
from tqdm import tqdm
from logging import debug, info, warning
from lib import helpers, lib, file, collection, database, filter
from lib.helpers import timeit
from lib.lib import empty_dirs


@click.group(invoke_without_command=False)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Folder scanning'''
    lib.raise_limits()
    ctx.obj.db = collection.Collection(**kwargs)


@timeit
async def fullscan(ctx, folders):
    files = [f for f in lib.find_files(list(folders)) if f[1].endswith(tuple(filter.default_formats))]
    # musics = []
    with tqdm(total=len(files) * 2, file=sys.stdout, desc="Loading music", leave=True, position=0, disable=ctx.obj.config.quiet) as bar:
        async def insert(semaphore, f):
            async with semaphore:
                try:
                    m = file.File(f[1], f[0])
                    if ctx.obj.crawl:
                        await m.find_youtube()
                        bar.update(1)
                    await ctx.obj.db.upsert(m)
                    bar.update(1)
                    # musics.append(m)
                    # musics.append((m.artist, m.album, m.genre, m.folder, m.youtube, m.number, m.rating, m.duration, m.size, m.title, m.path, m.keywords), )
                    # await ctx.obj.db.append(m.to_list())
                except asyncpg.exceptions.CheckViolationError as e:
                    warning("Violation: {}".format(e))
        semaphore = asyncio.BoundedSemaphore(ctx.obj.concurrency)
        debug('Gathering futures')
        tasks = [asyncio.ensure_future(insert(semaphore, f)) for f in files]
        await asyncio.gather(*tasks)


@cli.command()
@helpers.coro
@helpers.add_options(helpers.concurrency)
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
@click.argument('folders', nargs=-1)
@click.pass_context
async def scan(ctx, concurrency, crawl, folders, **kwargs):
    '''Load musics files in database'''
    ctx.obj.concurrency = concurrency
    ctx.obj.crawl = crawl
    debug('Concurrency: {}'.format(concurrency))
    await fullscan(ctx, folders)


@cli.command()
@helpers.coro
@helpers.add_options(helpers.concurrency)
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
@click.pass_context
async def rescan(ctx, concurrency, crawl, **kwargs):
    '''Rescan all folders registered in database'''
    folders = await ctx.obj.db.folders()
    ctx.obj.concurrency = concurrency
    ctx.obj.crawl = crawl
    debug('Concurrency: {}'.format(concurrency))
    await fullscan(ctx, [f['name'] for f in folders])


@cli.command()
@helpers.coro
@click.pass_context
async def watch(ctx, **kwargs):
    folders = await ctx.obj.db.folders()
    from hachiko.hachiko import AIOEventHandler

    class MusicWatcherHandler(AIOEventHandler):

        def __init__(self, loop=None):
            super().__init__(loop)

        async def update(self, path):
            for folder in folders:
                if path.startswith(folder['name']) and path.endswith(tuple(filter.default_formats)):
                    f = file.File(path, folder['name'])
                    await ctx.obj.db.upsert(f)
                    break

        async def on_modified(self, event):
            debug('Modifying DB for: {} {}'.format(event.src_path, event.event_type))
            await self.update(event.src_path)

        async def on_created(self, event):
            debug('Creating entry DB for: {} {}'.format(event.src_path, event.event_type))
            await self.update(event.src_path)

        async def on_deleted(self, event):
            debug('Deleting entry in DB for: {} {}'.format(event.src_path, event.event_type))
            await ctx.obj.db.delete(event.src_path)

        async def on_moved(self, event):
            debug('Moving entry in DB for: {} {}'.format(event.src_path, event.event_type))
            await ctx.obj.db.delete(event.src_path)
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


@cli.command()
@click.argument('folders', nargs=-1)
@click.pass_context
def find(ctx, folders, **kwargs):
    '''Only list files in selected folders'''
    files = lib.find_files(folders)
    for f in files:
        print(f[1])


@cli.command()
@helpers.coro
@helpers.add_options(filter.options)
@click.argument('destination')
@click.pass_context
async def sync(ctx, destination, **kwargs):
    '''Copy selected musics with filters to destination folder'''
    info('Destination: {}'.format(destination))
    ctx.obj.mf = filter.Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)

    files = lib.all_files(destination)
    destinations = {f[len(destination) + 1:]: f for f in files}
    sources = {m['path'][len(m['folder']) + 1:]: m['path'] for m in musics}
    to_delete = set(destinations.keys()) - set(sources.keys())
    to_copy = set(sources.keys()) - set(destinations.keys())
    with tqdm(total=len(to_delete), file=sys.stdout, desc="Deleting music", leave=True, position=0, disable=ctx.obj.config.quiet) as bar:
        for d in to_delete:
            if not ctx.obj.config.dry:
                info("Deleting {}".format(destinations[d]))
                os.remove(destinations[d])
            else:
                info("[DRY-RUN] False Deleting {}".format(destinations[d]))
            bar.update(1)
    with tqdm(total=len(to_copy), file=sys.stdout, desc="Copying music", leave=True, position=0, disable=ctx.obj.config.quiet) as bar:
        from shutil import copyfile
        for c in sorted(to_copy):
            final_destination = os.path.join(destination, c)
            if not ctx.obj.config.dry:
                info("Copying {} to {}".format(sources[c], final_destination))
                os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                copyfile(sources[c], final_destination)
            else:
                info("[DRY-RUN] False Copying {} to {}".format(sources[c], final_destination))
            bar.update(1)

    import shutil
    for d in empty_dirs(destination):
        if not ctx.obj.config.dry:
            shutil.rmtree(d)
        info("[DRY-RUN] Removing empty dir {}".format(d))
