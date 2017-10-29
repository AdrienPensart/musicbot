# -*- coding: utf-8 -*-
import click
import codecs
import os
from lib import helpers, database, playlist
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
@helpers.add_options(helpers.playlist_options)
@helpers.add_options(helpers.filter_options)
async def bests(ctx, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    playlists = await ctx.obj.db.bests(ctx.obj.mf)
    ctx.obj.playlist = playlist.Playlist(**kwargs)
    for p in playlists:
        playlist_filepath = os.path.join(ctx.obj.playlist.path, p['name'])
        with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
            debug('{} {}'.format(playlist_filepath, p['content']))
            playlist_file.write(p['content'])


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(helpers.playlist_options)
@helpers.add_options(helpers.filter_options)
async def new(ctx, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    p = await ctx.obj.db.playlist(ctx.obj.mf)
    print(p['content'])
    # ctx.obj.playlist = playlist.Playlist(**kwargs)
    # musics = await ctx.obj.db.filter(ctx.obj.mf)
    # ctx.obj.playlist.generate(musics, ctx.obj.mf)
