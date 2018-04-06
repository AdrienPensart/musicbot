# -*- coding: utf-8 -*-
import click
from lib import helpers, collection, database, mfilter


default_fields = ['title', 'album', 'artist', 'genre', 'path', 'keywords', 'folder', 'rating', 'number', 'folder', 'youtube', 'duration', 'size']
tag = [
    click.option('--fields', envvar='MB_FIELDS', help='Show only those fields', default=default_fields, multiple=True),
    # click.option('--output', envvar='MB_OUTPUT', help='Tags output format'),
]


@click.group()
@helpers.add_options(database.options)
@helpers.add_options(mfilter.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Music tags management'''
    ctx.obj.db = collection.Collection(**kwargs)
    ctx.obj.mf = mfilter.Filter(**kwargs)


@cli.command()
@helpers.coro
@helpers.add_options(tag)
@click.pass_context
async def show(ctx, fields, **kwargs):
    '''Show tags of musics with filters'''
    ctx.obj.musics = await ctx.obj.db.musics(ctx.obj.mf)
    for m in ctx.obj.musics:
        print([m[f] for f in fields])


# @cli.command()
# @helpers.coro
# @helpers.add_options(file.options)
# @click.pass_context
# async def update(ctx, **kwargs):
#     ctx.obj.musics = await ctx.obj.db.musics(ctx.obj.mf)
#     '''Add tags - Not Implemented'''
#     print(ctx.obj.musics)
