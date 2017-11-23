# -*- coding: utf-8 -*-
import click
from lib import helpers, options, database
from lib.filter import Filter


@click.group(invoke_without_command=True)
@helpers.coro
@options.add_options(options.db)
@options.add_options(options.filters)
@click.pass_context
async def cli(ctx, **kwargs):
    '''Generate some stats for music collection with filters'''
    ctx.obj.db = database.DbContext(**kwargs)
    ctx.obj.mf = Filter(**kwargs)
    stats = await ctx.obj.db.stats(ctx.obj.mf)
    print("Music    :", stats['musics'])
    print("Artist   :", stats['artists'])
    print("Album    :", stats['albums'])
    print("Genre    :", stats['genres'])
    print("Keywords :", stats['keywords'])
    from datetime import timedelta
    print("Total duration :", str(timedelta(seconds=stats['duration'])))
