# -*- coding: utf-8 -*-
import click
from datetime import timedelta
from lib import helpers, collection, database, filter
from lib.lib import bytesToHuman


@click.group(invoke_without_command=True)
@helpers.coro
@helpers.add_options(database.options)
@helpers.add_options(filter.options)
@click.pass_context
async def cli(ctx, **kwargs):
    '''Generate some stats for music collection with filters'''
    ctx.obj.db = collection.Collection(**kwargs)
    ctx.obj.mf = filter.Filter(**kwargs)
    stats = await ctx.obj.db.stats(ctx.obj.mf)
    print("Music    :", stats['musics'])
    print("Artist   :", stats['artists'])
    print("Album    :", stats['albums'])
    print("Genre    :", stats['genres'])
    print("Keywords :", stats['keywords'])
    print("Size     :", bytesToHuman(stats['size']))
    print("Total duration :", str(timedelta(seconds=stats['duration'])))
