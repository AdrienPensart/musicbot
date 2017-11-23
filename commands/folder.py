# -*- coding: utf-8 -*-
import click
import sys
import os
import asyncio
from tqdm import tqdm
from logging import debug, info
from lib import options, helpers, lib, file, database, filter
from lib.filter import Filter
from lib.lib import empty_dirs


@click.group(invoke_without_command=False)
@options.add_options(options.db)
@click.pass_context
def cli(ctx, **kwargs):
    '''Folder scanning'''
    ctx.obj.db = database.DbContext(**kwargs)


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
@options.add_options(options.filters)
@click.argument('destination')
@click.pass_context
async def sync(ctx, destination, **kwargs):
    '''Copy selected musics with filters to destination folder'''
    info('Destination: {}'.format(destination))
    ctx.obj.mf = Filter(**kwargs)
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


@cli.command()
@helpers.coro
@click.argument('folders', nargs=-1)
@click.pass_context
async def scan(ctx, folders, **kwargs):
    '''Load musics files in database'''
    lib.raise_limits()
    files = list(lib.find_files(list(folders)))
    # musics = []
    with tqdm(total=len(files), file=sys.stdout, desc="Loading music", leave=True, position=0, disable=ctx.obj.config.quiet) as bar:
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
    '''Rescan all folders registered in database'''
    folders = await ctx.obj.db.folders()
    for folder in folders:
        info('rescanning {}'.format(folder))


@cli.command()
@helpers.coro
@click.pass_context
async def watch(ctx, **kwargs):
    '''Check file modification in realtime and updates database'''
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
