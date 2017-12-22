# -*- coding: utf-8 -*- import click
import click
from lib import youtube, helpers, database, filter
from logging import debug
from tqdm import tqdm


@click.group()
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Youtube management'''
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(filter.options)
async def musics(ctx, **kwargs):
    '''Fetch youtube links for each music'''
    mf = filter.Filter(**kwargs)
    musics = await ctx.obj.db.filter(mf)
    with tqdm(desc='Youtube musics', total=len(musics), disable=ctx.obj.config.quiet) as bar:
        for m in musics:
            bar.update(1)
            result = youtube.search(m['artist'], m['title'], m['duration'])
            debug(m['artist'], m['title'], m['duration'], result)
            await ctx.obj.db.set_music_youtube(m['path'], result)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(filter.options)
async def albums(ctx, **kwargs):
    '''Fetch youtube links for each album'''
    mf = filter.Filter(**kwargs)
    albums = await ctx.obj.db.albums(mf)
    with tqdm(desc='Youtube albums', total=len(albums), disable=ctx.obj.config.quiet) as bar:
        for a in albums:
            bar.update(1)
            result = youtube.search(a['artist'], a['name'] + ' full album', a['duration'])
            debug(a['artist'], a['name'], a['duration'], result)
            await ctx.obj.db.set_album_youtube(a['id'], result)

# async def search_local(m):
#     bar.update(1)
#     m = dict(m)
#     result = youtube.search(m['artist'], m['title'], m['duration'])
#     m['youtube'] = result
#     debug(m['artist'], m['title'], m['duration'], m['youtube'])
#     await ctx.obj.db.upsert(m)
#     return m
# from multiprocessing.pool import ThreadPool
# pool = ThreadPool(1)
# musics = pool.imap_unordered(search_local, musics)
