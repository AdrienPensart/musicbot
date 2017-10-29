# -*- coding: utf-8 -*-
import click
from lib import helpers, database, filter, playlist
from logging import debug


@click.group(invoke_without_command=True)
@helpers.add_options(helpers.filter_options)
@helpers.add_options(helpers.db_options)
@click.pass_context
def cli(ctx, **kwargs):
    debug('playlist cli')
    debug(kwargs)
    ctx.obj.mf = filter.Filter(**kwargs)
    ctx.obj.db = database.DbContext(**kwargs)
    ctx.obj.playlist = playlist.Playlist(**kwargs)


@cli.command()
@click.pass_context
def bests(ctx, **kwargs):
    pass


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(helpers.playlist_options)
async def new(ctx, **kwargs):
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    ctx.obj.playlist.generate(musics, ctx.obj.mf)
