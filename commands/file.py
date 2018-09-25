import click
import logging
from lib import file, helpers, database, mfilter
from lib.collection import Collection

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.coro
@helpers.add_options(database.options)
@click.pass_context
async def cli(ctx, **kwargs):
    '''Music tags management'''
    ctx.obj.db = await Collection.make(**kwargs)


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(mfilter.options)
async def show(ctx, **kwargs):
    '''Show tags of musics with filters'''
    ctx.obj.mf = mfilter.Filter(**kwargs)
    ctx.obj.musics = await ctx.obj.db.musics(ctx.obj.mf)
    for m in ctx.obj.musics:
        f = file.File(m['path'])
        print(f.to_list())


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(file.options)
@helpers.add_options(mfilter.options)
async def update(ctx, **kwargs):
    ctx.obj.mf = mfilter.Filter(**kwargs)
    ctx.obj.musics = await ctx.obj.db.musics(ctx.obj.mf)
    logger.debug(kwargs)
    for m in ctx.obj.musics:
        f = file.File(m['path'])
        f.keywords = kwargs['keywords']
        f.artist = kwargs['artist']
        f.album = kwargs['album']
        f.title = kwargs['title']
        f.genre = kwargs['genre']
        f.number = kwargs['number']
        f.rating = kwargs['rating']
        f.save()
