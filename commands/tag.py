# -*- coding: utf-8 -*-
import click
from lib import helpers, options, database
from lib.filter import Filter


@click.group()
@options.add_options(options.db)
@click.pass_context
def cli(ctx, **kwargs):
    '''Music tags management'''
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@helpers.coro
@options.add_options(options.filters)
@options.add_options(options.tag)
@click.pass_context
async def show(ctx, fields, **kwargs):
    '''Show tags of musics with filters'''
    ctx.obj.mf = Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    for m in musics:
        print([m[f] for f in fields])


@cli.command()
@helpers.coro
@options.add_options(options.filters)
@click.pass_context
async def add(ctx, **kwargs):
    '''Add tags - Not Implemented'''
    ctx.obj.mf = Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    print(musics)


@cli.command()
@helpers.coro
@options.add_options(options.filters)
@click.pass_context
async def delete(ctx, *kwargs):
    '''Delete tags - Not implemented'''
    ctx.obj.mf = Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    print(musics)
