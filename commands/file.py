# -*- coding: utf-8 -*-
import click
from lib import file, helpers, collection, database, filter
from logging import debug


@click.group()
@helpers.add_options(database.options)
@helpers.add_options(filter.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Music tags management'''
    ctx.obj.db = collection.Collection(**kwargs)
    ctx.obj.mf = filter.Filter(**kwargs)


@cli.command()
@helpers.coro
@click.pass_context
async def show(ctx, **kwargs):
    '''Show tags of musics with filters'''
    ctx.obj.musics = await ctx.obj.db.musics(ctx.obj.mf)
    for m in ctx.obj.musics:
        f = file.File(m['path'])
        print(f.to_list())


@cli.command()
@helpers.coro
@helpers.add_options(file.options)
@click.pass_context
async def update(ctx, **kwargs):
    ctx.obj.musics = await ctx.obj.db.musics(ctx.obj.mf)
    debug(kwargs)
    for m in ctx.obj.musics:
        f = file.File(m['path'])
        f.keywords = kwargs['keywords']
        f.artist = kwargs['artist']
        f.album = kwargs['album']
        f.title = kwargs['title']
        f.genre = kwargs['genre']
        f.number = kwargs['number']
        f.rating = kwargs['rating']
        f.save()
