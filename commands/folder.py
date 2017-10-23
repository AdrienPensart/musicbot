# -*- coding: utf-8 -*-
import click
import sys
from tqdm import tqdm
from logging import debug, info
from lib import helpers, lib, file


@click.group(invoke_without_command=False)
@helpers.add_options(helpers.db_options)
@click.pass_context
def cli(ctx, host, port, user, password, db, **kwargs):
    debug('folder cli')
    db = helpers.DbContext(host=host, port=port, user=user, password=password, database=db)
    ctx.obj.db = db


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
    files = list(lib.find_files(list(folders)))
    with tqdm(total=len(files), file=sys.stdout, desc="Music loading", leave=True, position=0, disable=ctx.obj.config.quiet) as bar:
        for f in files:
            if f[1].endswith(tuple(lib.default_formats)):
                m = file.MusicFile(f[1], f[0])
                await ctx.obj.db.update(m)
            bar.update(1)


@cli.command()
@helpers.add_options(helpers.filter_options)
@helpers.coro
@click.pass_context
async def rescan(ctx, **kwargs):
    folders = await ctx.obj.db.folders()
    for folder in folders:
        info('rescanning {}'.format(folder))
