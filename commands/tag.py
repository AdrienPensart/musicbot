# -*- coding: utf-8 -*-
import click
from lib import helpers, database
from lib.filter import Filter


@click.group(invoke_without_command=False)
@helpers.add_options(helpers.db_options)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@helpers.coro
@helpers.add_options(helpers.filter_options)
@helpers.add_options(helpers.tag_options)
@click.pass_context
async def show(ctx, fields, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    for m in musics:
        print([m[f] for f in fields])


@cli.command()
@helpers.coro
@helpers.add_options(helpers.filter_options)
@click.pass_context
async def add(ctx, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    print(musics)


@cli.command()
@helpers.coro
@helpers.add_options(helpers.filter_options)
@click.pass_context
async def delete(ctx, *kwargs):
    ctx.obj.mf = Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    print(musics)
