# -*- coding: utf-8 -*-
import click
from lib import helpers, collection, database, mfilter
from click_didyoumean import DYMGroup


default_fields = ['title', 'album', 'artist', 'genre', 'path', 'keywords', 'folder', 'rating', 'number', 'folder', 'youtube', 'duration', 'size']
tag = [
    click.option('--fields', envvar='MB_FIELDS', help='Show only those fields', default=default_fields, multiple=True),
    # click.option('--output', envvar='MB_OUTPUT', help='Tags output format'),
]


@click.group(cls=DYMGroup)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Music tags management'''
    ctx.obj.db = collection.Collection(**kwargs)


@cli.command()
@helpers.coro
@helpers.add_options(tag)
@helpers.add_options(mfilter.options)
@click.pass_context
async def show(ctx, fields, **kwargs):
    '''Show tags of musics with filters'''
    mf = mfilter.Filter(**kwargs)
    musics = await ctx.obj.db.musics(mf)
    for m in musics:
        print([m[f] for f in fields])


# @cli.command()
# @helpers.coro
# @helpers.add_options(file.options)
# @helpers.add_options(mfilter.options)
# @click.pass_context
# async def update(ctx, **kwargs):
#     '''Add tags - Not Implemented'''
#     mf = mfilter.Filter(**kwargs)
#     musics = await ctx.obj.db.musics(mf)
#     print(musics)
