# -*- coding: utf-8 -*- import click
import click
from lib import helpers, database, collection, mfilter
from click_didyoumean import DYMGroup


@click.group(cls=DYMGroup)
@helpers.add_options(database.options)
@helpers.add_options(mfilter.options)
@helpers.add_options(helpers.concurrency)
@click.pass_context
def cli(ctx, concurrency, **kwargs):
    '''Youtube management'''
    ctx.obj.db = collection.Collection(**kwargs)
    ctx.obj.mf = mfilter.Filter(**kwargs)
    ctx.obj.concurrency = concurrency


@cli.command()
@click.pass_context
@helpers.coro
async def musics(ctx, **kwargs):
    '''Fetch youtube links for each music'''
    if ctx.obj.mf.youtube is None:
        ctx.obj.mf.youtube = ''
    await helpers.crawl_musics(ctx.obj.db, ctx.obj.mf, concurrency=ctx.obj.concurrency)


@cli.command()
@click.pass_context
@helpers.coro
@click.option('--youtube-album', envvar='MB_YOUTUBE_ALBUM', help='Select albums with a youtube link', default='')
async def albums(ctx, youtube_album, **kwargs):
    '''Fetch youtube links for each album'''
    await helpers.crawl_albums(ctx.obj.db, ctx.obj.mf, youtube_album=youtube_album, concurrency=ctx.obj.concurrency)
