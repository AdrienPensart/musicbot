# -*- coding: utf-8 -*-
import click
import codecs
import os
from textwrap import indent
from tqdm import tqdm
import sys
from lib import helpers, database
from logging import info
from lib.filter import Filter
from lib import options
from logging import debug


@click.group(invoke_without_command=False)
@options.add_options(options.db)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@options.add_options(options.filters)
@click.argument('path', type=click.Path(exists=True))
@click.option('--prefix', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', help="Append this suffix to playlist name", default='')
async def bests(ctx, path, prefix, suffix, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
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
@options.add_options(options.filters)
@click.argument('path', type=click.File('w'), default='-')
@click.option('--prefix', help="Append prefix before each path (implies relative)", default='')
async def new(ctx, path, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    p = await ctx.obj.db.playlist(ctx.obj.mf)
    print(p['content'], file=path)
