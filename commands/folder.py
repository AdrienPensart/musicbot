# -*- coding: utf-8 -*-
import click
import sys
import os
import asyncio
from tqdm import tqdm
from logging import error, debug, info
from lib import helpers, lib, collection, database, filter
from lib.config import config
from lib.helpers import watcher, fullscan
from lib.lib import empty_dirs


@click.group(invoke_without_command=False)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Folder scanning'''
    lib.raise_limits()
    ctx.obj.db = collection.Collection(**kwargs)


@cli.command()
@helpers.coro
@click.argument('folders', nargs=-1)
@click.pass_context
async def new(ctx, folders, **kwargs):
    '''Add a new folder in database'''
    tasks = [asyncio.ensure_future(ctx.obj.db.new_folder(f)) for f in folders]
    await asyncio.gather(*tasks)


@cli.command()
@helpers.coro
@click.pass_context
async def list(ctx, **kwargs):
    '''List existing folders'''
    folders = await ctx.obj.db.folders()
    for f in folders:
        print(f['name'])


@cli.command()
@helpers.coro
@helpers.add_options(helpers.concurrency)
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
@click.argument('folders', nargs=-1)
@click.pass_context
async def scan(ctx, concurrency, crawl, folders, **kwargs):
    '''Load musics files in database'''
    debug('Concurrency: {}'.format(concurrency))
    await fullscan(ctx.obj.db, folders=folders, concurrency=concurrency, crawl=crawl)


@cli.command()
@helpers.coro
@helpers.add_options(helpers.concurrency)
@helpers.add_options(helpers.concurrency)
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
@click.pass_context
async def rescan(ctx, concurrency, crawl, **kwargs):
    '''Rescan all folders registered in database'''
    debug('Concurrency: {}'.format(concurrency))
    await fullscan(ctx.obj.db, concurrency=concurrency, crawl=crawl)


@cli.command()
@helpers.coro
@click.pass_context
async def watch(ctx, **kwargs):
    '''Watch files changes in folders'''
    await watcher(ctx.obj.db)


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
    musics = await ctx.obj.db.musics(ctx.obj.mf)

    files = lib.all_files(destination)
    destinations = {f[len(destination) + 1:]: f for f in files}
    sources = {m['path'][len(m['folder']) + 1:]: m['path'] for m in musics}
    to_delete = set(destinations.keys()) - set(sources.keys())
    to_copy = set(sources.keys()) - set(destinations.keys())
    with tqdm(total=len(to_delete), file=sys.stdout, desc="Deleting music", leave=True, position=0, disable=config.quiet) as bar:
        for d in to_delete:
            if not config.dry:
                try:
                    info("Deleting {}".format(destinations[d]))
                    os.remove(destinations[d])
                except Exception as e:
                    error(e)
            else:
                info("[DRY-RUN] False Deleting {}".format(destinations[d]))
            bar.update(1)
    with tqdm(total=len(to_copy), file=sys.stdout, desc="Copying music", leave=True, position=0, disable=config.quiet) as bar:
        from shutil import copyfile
        for c in sorted(to_copy):
            final_destination = os.path.join(destination, c)
            if not config.dry:
                info("Copying {} to {}".format(sources[c], final_destination))
                os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                copyfile(sources[c], final_destination)
            else:
                info("[DRY-RUN] False Copying {} to {}".format(sources[c], final_destination))
            bar.update(1)

    import shutil
    for d in empty_dirs(destination):
        if not config.dry:
            shutil.rmtree(d)
        info("[DRY-RUN] Removing empty dir {}".format(d))
