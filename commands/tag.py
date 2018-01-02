# -*- coding: utf-8 -*-
import click
from lib import helpers, collection, database, filter


default_fields = ['title', 'album', 'artist', 'genre', 'path', 'keywords', 'folder', 'rating', 'number', 'folder', 'youtube', 'duration', 'size']
tag = [
    click.option('--fields', envvar='MB_FIELDS', help='Show only those fields', default=default_fields, multiple=True),
    # click.option('--output', envvar='MB_OUTPUT', help='Tags output format'),
]


@click.group()
@helpers.add_options(database.options)
@helpers.add_options(filter.options)
@click.pass_context
@helpers.coro
async def cli(ctx, **kwargs):
    '''Music tags management'''
    ctx.obj.db = collection.Collection(**kwargs)
    ctx.obj.mf = filter.Filter(**kwargs)


@cli.command()
@helpers.coro
@helpers.add_options(tag)
@click.pass_context
async def show(ctx, fields, **kwargs):
    '''Show tags of musics with filters'''
    ctx.obj.musics = await ctx.obj.db.musics(ctx.obj.mf)
    for m in ctx.obj.musics:
        print([m[f] for f in fields])


@cli.command()
@helpers.coro
@click.pass_context
async def add(ctx, **kwargs):
    '''Add tags - Not Implemented'''
    print(ctx.obj.musics)


@cli.command()
@helpers.coro
@click.pass_context
async def delete(ctx, *kwargs):
    '''Delete tags - Not implemented'''
    print(ctx.obj.musics)
