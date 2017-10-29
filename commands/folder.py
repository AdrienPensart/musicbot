# -*- coding: utf-8 -*-
import click
import sys
from tqdm import tqdm
from logging import debug, info
from lib import helpers, lib, file, database, filter


@click.group(invoke_without_command=False)
@helpers.add_options(helpers.db_options)
@click.pass_context
def cli(ctx, **kwargs):
    debug('folder cli')
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
@helpers.add_options(helpers.filter_options)
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
@helpers.add_options(helpers.filter_options)
@helpers.coro
@click.pass_context
async def rescan(ctx, **kwargs):
    folders = await ctx.obj.db.folders()
    for folder in folders:
        info('rescanning {}'.format(folder))
