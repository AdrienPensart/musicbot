import click
from datetime import timedelta
from lib import helpers, database, mfilter
from lib.collection import Collection
from lib.lib import bytes_to_human


@click.group(cls=helpers.GroupWithHelp)
@helpers.coro
@click.pass_context
@helpers.add_options(database.options)
async def cli(ctx, **kwargs):
    '''Youtube management'''
    ctx.obj.db = await Collection.make(**kwargs)


@cli.command()
@click.pass_context
@helpers.add_options(mfilter.options)
@helpers.coro
async def show(ctx, **kwargs):
    '''Generate some stats for music collection with filters'''
    ctx.obj.mf = mfilter.Filter(**kwargs)
    stats = await ctx.obj.db.stats(ctx.obj.mf)
    print("Music    :", stats['musics'])
    print("Artist   :", stats['artists'])
    print("Album    :", stats['albums'])
    print("Genre    :", stats['genres'])
    print("Keywords :", stats['keywords'])
    print("Size     :", bytes_to_human(stats['size']))
    print("Total duration :", str(timedelta(seconds=stats['duration'])))
