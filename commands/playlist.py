# -*- coding: utf-8 -*-
import click
import codecs
import os
from tqdm import tqdm
import sys
from lib import helpers, database
from logging import info
from lib.filter import Filter
from logging import debug


@click.group(invoke_without_command=False)
@helpers.add_options(helpers.db_options)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(helpers.filter_options)
@click.argument('path')
async def bests(ctx, path, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    debug(ctx.obj.mf.to_list())
    playlists = await ctx.obj.db.bests(ctx.obj.mf)
    with tqdm(total=len(playlists), file=sys.stdout, desc="Bests playlists", disable=ctx.obj.config.quiet) as bar:
        for p in playlists:
            playlist_filepath = os.path.join(path, p['name'])
            if not ctx.obj.config.dry:
                try:
                    with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                        debug('{} {}'.format(playlist_filepath, p['content']))
                        playlist_file.write(p['content'])
                except:
                    info('Unable to write playlist {}'.format(playlist_filepath))
            else:
                info('Writing playlist to {} with content {}'.format(playlist_filepath, p['content']))
            bar.update(1)


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(helpers.filter_options)
@click.argument('path', type=click.File('w'), default='-')
async def new(ctx, path, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    p = await ctx.obj.db.playlist(ctx.obj.mf)
    print(p['content'], file=path)
