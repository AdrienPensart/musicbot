import click
from click_didyoumean import DYMGroup
from datetime import timedelta
from lib import helpers, collection, database, mfilter
from lib.lib import bytesToHuman


@click.group(cls=DYMGroup)
@click.pass_context
@helpers.add_options(database.options)
def cli(ctx, **kwargs):
    '''Youtube management'''
    ctx.obj.db = collection.Collection(**kwargs)


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
    print("Size     :", bytesToHuman(stats['size']))
    print("Total duration :", str(timedelta(seconds=stats['duration'])))
