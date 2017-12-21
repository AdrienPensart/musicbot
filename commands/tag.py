# -*- coding: utf-8 -*-
import click
from lib import helpers, database, filter


default_fields = ['title', 'album', 'artist', 'genre', 'path', 'keywords', 'folder', 'rating', 'number', 'folder', 'youtube', 'duration', 'size']
tag = [
    click.option('--fields', envvar='MB_FIELDS', help='Show only those fields', default=default_fields, multiple=True),
    # click.option('--output', envvar='MB_OUTPUT', help='Tags output format'),
]


@click.group()
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Music tags management'''
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@helpers.coro
@helpers.add_options(tag)
@helpers.add_options(filter.options)
@click.pass_context
async def show(ctx, fields, **kwargs):
    '''Show tags of musics with filters'''
    mf = filter.Filter(**kwargs)
    musics = await ctx.obj.db.filter(mf)
    for m in musics:
        print([m[f] for f in fields])


@cli.command()
@helpers.coro
@helpers.add_options(filter.options)
@click.pass_context
async def add(ctx, **kwargs):
    '''Add tags - Not Implemented'''
    ctx.obj.mf = filter.Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    print(musics)


@cli.command()
@helpers.coro
@helpers.add_options(filter.options)
@click.pass_context
async def delete(ctx, *kwargs):
    '''Delete tags - Not implemented'''
    ctx.obj.mf = filter.Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    print(musics)
