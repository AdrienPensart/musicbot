import click
from musicbot.lib import helpers, database, mfilter


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.coro
@helpers.add_options(database.options)
async def cli(ctx, **kwargs):
    '''Youtube management'''
    ctx.obj.db = await database.Database.make(**kwargs)


@cli.command()
@click.pass_context
@helpers.add_options(mfilter.options)
@helpers.add_options(helpers.concurrency_options)
@helpers.coro
async def musics(ctx, concurrency, **kwargs):
    '''Fetch youtube links for each music'''
    mf = mfilter.Filter(**kwargs)
    concurrency = concurrency
    await helpers.crawl_musics(ctx.obj.db, mf=mf, concurrency=concurrency)


# @cli.command()
# @click.pass_context
# @helpers.add_options(mfilter.options)
# @helpers.add_options(helpers.concurrency_options)
# @helpers.coro
# @click.option('--youtube-album', envvar='MB_YOUTUBE_ALBUM', help='Select albums with a youtube link', default='')
# async def albums(ctx, concurrency, youtube_album, **kwargs):
#     '''Fetch youtube links for each album'''
#     mf = mfilter.Filter(**kwargs)
#     concurrency = concurrency
#     await helpers.crawl_albums(ctx.obj.db, mf=mf, youtube_album=youtube_album, concurrency=concurrency)
#
#
# @cli.command()
# @click.pass_context
# @helpers.coro
# async def only(ctx, **kwargs):
#     '''Fetch youtube links for each album'''
#     mf = mfilter.Filter(**kwargs)
#     results = await ctx.obj.db.fetch("""select * from do_filter($1::filters) where youtube like 'https://www.youtube.com/watch?v=%'""", mf.to_list())
#     for r in results:
#         print(r)
