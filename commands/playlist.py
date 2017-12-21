# -*- coding: utf-8 -*-
import click
import codecs
import os
import sys
from textwrap import indent
from tqdm import tqdm
from lib import helpers, database, filter
from logging import info, debug


@click.group()
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Playlist management'''
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(filter.options)
@click.argument('path', type=click.Path(exists=True))
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
async def bests(ctx, path, prefix, suffix, **kwargs):
    '''Generate bests playlists with some rules'''
    ctx.obj.mf = filter.Filter(**kwargs)
    if len(prefix):
        ctx.obj.mf.relative = True
    playlists = await ctx.obj.db.bests(ctx.obj.mf)
    with tqdm(total=len(playlists), file=sys.stdout, desc="Bests playlists", disable=ctx.obj.config.quiet) as bar:
        for p in playlists:
            playlist_filepath = os.path.join(path, p['name'] + suffix + '.m3u')
            if not ctx.obj.config.dry:
                try:
                    with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                        content = indent(p['content'], prefix, lambda line: line != '#EXTM3U')
                        debug('{} {}'.format(playlist_filepath, content))
                        playlist_file.write(content)
                except:
                    info('Unable to write playlist {}'.format(playlist_filepath))
            else:
                info('Writing playlist to {} with content {}'.format(playlist_filepath, p['content']))
            bar.update(1)


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(filter.options)
@click.argument('path', type=click.File('w'), default='-')
@click.option('--prefix', envvar='MB_SUFFIX', help="Append prefix before each path (implies relative)", default='')
async def new(ctx, path, **kwargs):
    '''Generate a new playlist'''
    ctx.obj.mf = filter.Filter(**kwargs)
    p = await ctx.obj.db.playlist(ctx.obj.mf)
    print(p['content'], file=path)
