# -*- coding: utf-8 -*-
import click
import codecs
import os
import sys
from click_didyoumean import DYMGroup
from textwrap import indent
from tqdm import tqdm
from lib import helpers, database, collection, mfilter
from lib.config import config
from logging import info, debug


@click.group(cls=DYMGroup)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Playlist management'''
    ctx.obj.db = collection.Collection(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(mfilter.options)
@click.argument('path', type=click.Path(exists=True))
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
async def bests(ctx, path, prefix, suffix, **kwargs):
    '''Generate bests playlists with some rules'''
    ctx.obj.mf = mfilter.Filter(**kwargs)
    if len(prefix):
        ctx.obj.mf.relative = True
    playlists = await ctx.obj.db.bests(ctx.obj.mf)

    with tqdm(total=len(playlists), file=sys.stdout, desc="Bests playlists", disable=config.quiet) as bar:
        for p in playlists:
            playlist_filepath = os.path.join(path, p['name'] + suffix + '.m3u')
            content = indent(p['content'], prefix, lambda line: line != '#EXTM3U')
            if not config.dry:
                try:
                    with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                        debug('Writing playlist to {} with content:\n{}'.format(playlist_filepath, content))
                        playlist_file.write(content)
                except Exception as e:
                    info('Unable to write playlist to: {}'.format(playlist_filepath))
            else:
                info('DRY RUN: Writing playlist to {} with content:\n{}'.format(playlist_filepath, content))
            bar.update(1)


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(mfilter.options)
@click.argument('path', type=click.File('w'), default='-')
async def new(ctx, path, **kwargs):
    '''Generate a new playlist'''
    ctx.obj.mf = mfilter.Filter(**kwargs)
    p = await ctx.obj.db.playlist(ctx.obj.mf)
    if not config.dry:
        print(p['content'], file=path)
    else:
        info('DRY RUN: Writing playlist to {} with content:\n{}'.format(path, p['content']))
